"""Operator-reviewed prices and authenticated access, independently expiring.

Only trusted local configuration belongs here; media/model outputs never set prices.
"""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json

SOURCE = 'https://ai.google.dev/gemini-api/docs/pricing'
RATES = {
    'standard': {'gemini-3.5-flash-lite': ['0.30', '2.50'],
                 'gemini-3.8-flash': ['0.75', '3.75']},
    'flex': {'gemini-3.5-flash-lite': ['0.15', '1.25'],
             'gemini-3.8-flash': ['0.375', '1.875']},
}


def fresh(value):
    checked = datetime.fromisoformat(value)
    if checked.tzinfo is None or not timedelta(0) <= datetime.now(timezone.utc) - checked <= timedelta(hours=24):
        raise ValueError('Model access and price reviews must each be within 24 hours')
    return checked


def reviewed_prices(policy_bytes):
    policy = json.loads(policy_bytes)
    if (policy.get('format') != 'svh.gemini-price-policy.v1'
            or policy.get('source') != SOURCE or policy.get('rates') != RATES
            or not isinstance(policy.get('review_note'), str) or not policy['review_note'].strip()):
        raise ValueError('Unsupported reviewed price policy; review code before changing rates')
    return policy, fresh(policy['checked_at'])


def access_entry(metadata, name):
    entries = [entry for entry in metadata['models'] if entry.get('model') == name]
    if len(entries) != 1:
        raise ValueError('Exactly one authenticated entry is required per model')
    entry = entries[0]
    if (entry.get('returned_name') != 'models/' + name
            or 'generateContent' not in entry.get('supported_actions', [])
            or any(type(entry.get(key)) is not int or entry[key] <= 0
                   for key in ('input_limit', 'output_limit'))):
        raise ValueError('Authenticated model access is unconfirmed')
    return entry


def reviewed_access(policy_bytes, metadata, name, tier):
    policy, price_checked = reviewed_prices(policy_bytes)
    if name not in RATES['standard'] or tier not in RATES:
        raise ValueError('Unreviewed model or service tier')
    if (metadata.get('format') != 'svh.gemini-access.v2'
            or metadata.get('price_policy_sha256') != sha256(policy_bytes).hexdigest()
            or metadata.get('generation_requests') != 0):
        raise ValueError('Authenticated access must bind the exact reviewed price policy')
    checked = min(price_checked, fresh(metadata['checked_at']))
    return access_entry(metadata, name), policy['rates'][tier][name], checked
