"""Renew authenticated limits after an explicit official-price review; no inference."""
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from google import genai
from google.genai.types import HttpOptions, HttpRetryOptions
from svh.gemini import private_values
from svh.model_policy import RATES, reviewed_prices, reviewed_access


def renew(root, client):
    policy_bytes = (root / 'notes/runs/gemini-price-policy.json').read_bytes()
    reviewed_prices(policy_bytes)  # Expired review cannot be refreshed by this command.
    report = {'format': 'svh.gemini-access.v2',
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'generation_requests': 0, 'models': [],
              'price_policy_sha256': sha256(policy_bytes).hexdigest()}
    for name in RATES['standard']:
        try:
            entry = client.models.get(model=name)
        except Exception as error:
            # Do not serialize provider errors/headers or overwrite usable evidence.
            raise RuntimeError('Authenticated metadata request failed: ' + type(error).__name__) from None
        report['models'].append({'model': name, 'returned_name': entry.name,
            'input_limit': entry.input_token_limit, 'output_limit': entry.output_token_limit,
            'supported_actions': entry.supported_actions})
        reviewed_access(policy_bytes, report, name, 'standard')
    if (root / 'notes/runs/gemini-price-policy.json').read_bytes() != policy_bytes:
        raise ValueError('Price policy changed during authenticated access review')
    destination = root / 'notes/runs/gemini-model-metadata.json'
    if destination.exists():
        previous = destination.read_bytes()
        archive = destination.with_name('gemini-model-metadata-' + sha256(previous).hexdigest() + '.json')
        if archive.exists() and archive.read_bytes() != previous:
            raise ValueError('Historical access evidence differs')
        archive.write_bytes(previous)
    temporary = destination.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(destination)
    return report


def main():
    root = Path(__file__).resolve().parents[1]
    # Check the operator's price review before even constructing the API client.
    reviewed_prices((root / 'notes/runs/gemini-price-policy.json').read_bytes())
    config = private_values(root / '.env')
    secrets = private_values(Path(config['SVH_GEMINI_SECRETS_FILE']))
    key = secrets.get('GEMINI_API_KEY') or secrets.get('GOOGLE_API_KEY')
    if not key:
        raise SystemExit('No authorized API key found')
    with genai.Client(api_key=key, vertexai=False, http_options=HttpOptions(
            base_url='https://generativelanguage.googleapis.com', api_version='v1beta',
            timeout=30_000, retry_options=HttpRetryOptions(attempts=1))) as client:
        try:
            report = renew(root, client)
        except Exception as error:
            raise SystemExit('Metadata renewal failed: ' + type(error).__name__) from None
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
