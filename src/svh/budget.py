"""Persistent, fail-closed request reservations. This module never calls an API.

Unknown outcomes retain their full reservation. Only a received, metered result
may settle for less. All values are integer microdollars, rounded upward.
"""

from contextlib import contextmanager
from decimal import Decimal, ROUND_CEILING
import os
from pathlib import Path
import sqlite3
import uuid


class BudgetExceeded(RuntimeError):
    pass


def microdollars(usd):
    value = Decimal(str(usd))
    if not value.is_finite() or value < 0:
        raise ValueError("Cost must be finite and nonnegative")
    return int((value * 1_000_000).to_integral_value(rounding=ROUND_CEILING))


def token_cost(input_tokens, output_tokens, input_usd_per_million, output_usd_per_million):
    """Include all billable output, including reasoning, in output_tokens."""
    if any(type(n) is not int or n < 0 for n in (input_tokens, output_tokens)):
        raise ValueError("Token counts must be nonnegative integers")
    rates = [Decimal(str(rate)) for rate in (input_usd_per_million, output_usd_per_million)]
    if any(not rate.is_finite() or rate < 0 for rate in rates):
        raise ValueError("Prices must be finite and nonnegative")
    return int((input_tokens * rates[0] + output_tokens * rates[1]).to_integral_value(rounding=ROUND_CEILING))


class Budget:
    @classmethod
    def existing(cls, path: Path):
        """Open an initialized ledger without changing its spending limit."""
        instance = cls.__new__(cls)
        instance.path = Path(path)
        with sqlite3.connect(f'{instance.path.resolve().as_uri()}?mode=ro', uri=True) as db:
            if db.execute('SELECT cap FROM policy WHERE id=1').fetchone() is None:
                raise ValueError('Budget has not been initialized')
        return instance

    def __init__(self, path: Path, cap_usd):
        self.path = Path(path)
        cap = microdollars(cap_usd)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(descriptor)
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY CHECK(id=1), cap INTEGER NOT NULL)")
            db.execute("INSERT OR IGNORE INTO policy VALUES (1, ?)", (cap,))
            # Restart/config changes may tighten the cap, never silently raise it.
            db.execute("UPDATE policy SET cap=min(cap, ?) WHERE id=1", (cap,))
            db.execute("""CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY, label TEXT NOT NULL, reserved INTEGER NOT NULL,
                charged INTEGER NOT NULL, state TEXT NOT NULL)""")

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def reserve(self, maximum_microdollars: int, *, label: str):
        if type(maximum_microdollars) is not int or maximum_microdollars <= 0:
            raise ValueError("A positive integer worst-case reservation is required")
        if not label or len(label) > 200:
            raise ValueError("A short non-secret request label is required")
        request = uuid.uuid4().hex
        with self.transaction() as db:
            cap = db.execute("SELECT cap FROM policy WHERE id=1").fetchone()[0]
            total = db.execute("SELECT coalesce(sum(charged),0) FROM requests").fetchone()[0]
            if total + maximum_microdollars > cap:
                raise BudgetExceeded("Request would exceed the remaining local API budget")
            db.execute("INSERT INTO requests VALUES (?, ?, ?, ?, 'reserved')",
                       (request, label, maximum_microdollars, maximum_microdollars))
        return request

    def authorize_limit(self, cap_usd, *, expected_cap_usd, authorization: str):
        """Explicit owner funding event; preserve every past charge/reservation."""
        cap, expected = microdollars(cap_usd), microdollars(expected_cap_usd)
        if cap <= expected or not authorization.strip() or len(authorization) > 300:
            raise ValueError('A higher limit and a short non-secret owner authorization reference are required')
        with self.transaction() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS funding (
                authorization TEXT PRIMARY KEY, previous_cap INTEGER NOT NULL,
                authorized_cap INTEGER NOT NULL, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
            prior = db.execute('SELECT previous_cap, authorized_cap FROM funding WHERE authorization=?', (authorization,)).fetchone()
            if prior is not None:
                if prior != (expected, cap):
                    raise ValueError('Authorization already recorded with different amounts')
                return
            current = db.execute('SELECT cap FROM policy WHERE id=1').fetchone()[0]
            if current != expected:
                raise ValueError('Spending limit changed; review before authorizing funding')
            if db.execute("SELECT 1 FROM requests WHERE state='exceeded' LIMIT 1").fetchone():
                raise ValueError('Resolve the unexpected request overage before funding')
            db.execute('INSERT INTO funding(authorization,previous_cap,authorized_cap) VALUES (?,?,?)', (authorization, expected, cap))
            db.execute('UPDATE policy SET cap=? WHERE id=1', (cap,))

    def settle(self, request: str, actual_microdollars: int):
        if type(actual_microdollars) is not int or actual_microdollars < 0:
            raise ValueError("Metered cost must be a nonnegative integer")
        exceeded = False
        with self.transaction() as db:
            row = db.execute("SELECT reserved, charged, state FROM requests WHERE id=?", (request,)).fetchone()
            if row is None:
                raise ValueError("Unknown request reservation")
            reserved, charged, state = row
            if state != "reserved":
                if state == "settled" and charged == actual_microdollars:
                    return  # Idempotent acknowledgment, never a second call.
                raise ValueError("Request already finalized")
            exceeded = actual_microdollars > reserved
            db.execute("UPDATE requests SET charged=?, state=? WHERE id=?",
                       (actual_microdollars, "exceeded" if exceeded else "settled", request))
            if exceeded:
                db.execute("UPDATE policy SET cap=0 WHERE id=1")
        if exceeded:
            raise BudgetExceeded("Metered cost exceeded its reservation; further calls disabled")

    def summary(self):
        with self.transaction() as db:
            cap = db.execute("SELECT cap FROM policy WHERE id=1").fetchone()[0]
            total = db.execute("SELECT coalesce(sum(charged),0) FROM requests").fetchone()[0]
            pending = db.execute("SELECT count(*) FROM requests WHERE state='reserved'").fetchone()[0]
        return {"cap_microdollars": cap, "charged_or_reserved_microdollars": total,
                "available_microdollars": max(0, cap - total), "unsettled_requests": pending}
