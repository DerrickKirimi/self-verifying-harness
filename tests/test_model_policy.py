import importlib.util
import json
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from svh.model_policy import RATES, SOURCE, reviewed_access, reviewed_prices


def evidence(tmp_path):
    directory = tmp_path / 'notes/runs'
    directory.mkdir(parents=True)
    # Reviews may straddle midnight; neither review may be older than 24 hours.
    now = datetime.now(timezone.utc)
    policy = {'format': 'svh.gemini-price-policy.v1', 'source': SOURCE,
              'checked_at': (now - timedelta(hours=2)).isoformat(),
              'rates': RATES, 'review_note': 'Reviewed official prices'}
    raw = json.dumps(policy).encode()
    (directory / 'gemini-price-policy.json').write_bytes(raw)
    metadata = {'format': 'svh.gemini-access.v2', 'generation_requests': 0,
                'checked_at': now.isoformat(), 'price_policy_sha256': sha256(raw).hexdigest(),
                'models': [{'model': name, 'returned_name': 'models/' + name,
                            'input_limit': 1048576, 'output_limit': 65536,
                            'supported_actions': ['generateContent']} for name in RATES['standard']]}
    return raw, policy, metadata


def test_reviews_are_independent_and_use_oldest_expiry(tmp_path):
    raw, policy, metadata = evidence(tmp_path)
    for tier in RATES:
        entry, rates, checked = reviewed_access(raw, metadata, 'gemini-3.8-flash', tier)
        assert rates == RATES[tier]['gemini-3.8-flash']
        assert checked.isoformat() == policy['checked_at']
        assert entry['input_limit'] == 1048576


@pytest.mark.parametrize('kind', ['stale_price', 'future_price', 'naive_price', 'stale_access',
                                  'future_access', 'hash', 'rates', 'source', 'duplicate',
                                  'limit', 'action', 'alias', 'unknown_model', 'tier'])
def test_invalid_reviews_fail_closed(tmp_path, kind):
    raw, policy, metadata = evidence(tmp_path)
    name, tier = 'gemini-3.8-flash', 'standard'
    now = datetime.now(timezone.utc)
    if kind == 'stale_price': policy['checked_at'] = (now - timedelta(days=2)).isoformat()
    if kind == 'future_price': policy['checked_at'] = (now + timedelta(hours=1)).isoformat()
    if kind == 'naive_price': policy['checked_at'] = now.replace(tzinfo=None).isoformat()
    if kind == 'stale_access': metadata['checked_at'] = (now - timedelta(days=2)).isoformat()
    if kind == 'future_access': metadata['checked_at'] = (now + timedelta(hours=1)).isoformat()
    if kind == 'hash': metadata['price_policy_sha256'] = 'changed'
    if kind == 'rates': policy['rates'] = {'standard': {name: ['0', '0']}}
    if kind == 'source': policy['source'] = 'https://untrusted.invalid/prices'
    if kind == 'duplicate': metadata['models'].append(dict(metadata['models'][-1]))
    if kind == 'limit': metadata['models'][-1]['input_limit'] = True
    if kind == 'action': metadata['models'][-1]['supported_actions'] = []
    if kind == 'alias': metadata['models'][-1]['returned_name'] = 'models/alias'
    if kind == 'unknown_model': name = 'unknown'
    if kind == 'tier': tier = 'priority'
    raw = json.dumps(policy).encode()
    if kind != 'hash': metadata['price_policy_sha256'] = sha256(raw).hexdigest()
    with pytest.raises(ValueError): reviewed_access(raw, metadata, name, tier)


def probe_module():
    spec = importlib.util.spec_from_file_location('probe_gemini', Path(__file__).resolve().parents[1] / 'scripts/probe_gemini.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_partial_probe_preserves_old_metadata_and_redacts_error(tmp_path):
    raw, policy, metadata = evidence(tmp_path)
    path = tmp_path / 'notes/runs/gemini-model-metadata.json'
    path.write_bytes(b'previous evidence')
    entry = metadata['models'][0]
    client = Mock()
    client.models.get.side_effect = [SimpleNamespace(name=entry['returned_name'], input_token_limit=1048576,
        output_token_limit=65536, supported_actions=['generateContent']), RuntimeError('SECRET')]
    with pytest.raises(RuntimeError) as error: probe_module().renew(tmp_path, client)
    assert 'SECRET' not in str(error.value)
    assert path.read_bytes() == b'previous evidence'
    assert client.models.get.call_count == 2


def test_successful_probe_binds_review_and_archives_previous_metadata(tmp_path):
    raw, policy, metadata = evidence(tmp_path)
    path = tmp_path / 'notes/runs/gemini-model-metadata.json'
    path.write_bytes(b'previous evidence')
    client = Mock()
    client.models.get.side_effect = [SimpleNamespace(name=e['returned_name'], input_token_limit=1048576,
        output_token_limit=65536, supported_actions=['generateContent']) for e in metadata['models']]
    report = probe_module().renew(tmp_path, client)
    assert report == json.loads(path.read_text())
    assert report['price_policy_sha256'] == sha256(raw).hexdigest()
    assert report['generation_requests'] == 0
    assert (path.parent / ('gemini-model-metadata-' + sha256(b'previous evidence').hexdigest() + '.json')).read_bytes() == b'previous evidence'


def test_configured_factory_uses_review_without_increasing_ledger(tmp_path):
    from svh.budget import Budget
    from svh.gemini import configured_model
    raw, policy, metadata = evidence(tmp_path)
    (tmp_path / 'notes/runs/gemini-model-metadata.json').write_text(json.dumps(metadata))
    secret = tmp_path / 'secret'
    secret.write_text('GEMINI_API_KEY=test-not-a-key\n'); secret.chmod(0o600)
    config = tmp_path / '.env'
    config.write_text('SVH_GEMINI_SECRETS_FILE=' + str(secret) + '\nSVH_API_CAP_USD=99\n'); config.chmod(0o600)
    budget = Budget(tmp_path / 'data/runtime/gemini-budget.sqlite', '2')
    budget.reserve(500000, label='unknown')
    with patch('svh.gemini.model', return_value='constructed') as factory:
        assert configured_model(tmp_path, name='gemini-3.8-flash') == 'constructed'
        assert factory.call_args.kwargs['price'].input_rate == '0.75'
    assert budget.summary() == {'cap_microdollars': 2000000, 'charged_or_reserved_microdollars': 500000,
                                'available_microdollars': 1500000, 'unsettled_requests': 1}
