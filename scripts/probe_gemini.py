"""Read authenticated model metadata only; no generate/count/upload calls."""
import json
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai.types import HttpOptions, HttpRetryOptions
from svh.gemini import private_values

root = Path(__file__).resolve().parents[1]
config = private_values(root / ".env")
secrets = private_values(Path(config["SVH_GEMINI_SECRETS_FILE"]))
key = secrets.get("GEMINI_API_KEY") or secrets.get("GOOGLE_API_KEY")
if not key:
    raise SystemExit("No authorized API key found")

report = {"checked_at": datetime.now(timezone.utc).isoformat(),
          "generation_requests": 0, "models": [],
          "pricing_source": "https://ai.google.dev/gemini-api/docs/pricing",
          "pricing_checked_date": "2026-10-20"}
with genai.Client(api_key=key, vertexai=False, http_options=HttpOptions(
        base_url="https://generativelanguage.googleapis.com", api_version="v1beta",
        timeout=30_000, retry_options=HttpRetryOptions(attempts=1))) as client:
    for name, input_rate, output_rate in [("gemini-3.5-flash-lite", "0.30", "2.50"),
                                           ("gemini-3.8-flash", "0.75", "3.75")]:
        try:
            metadata = client.models.get(model=name)
        except Exception as error:
            # Provider exception text may include credentials or account details.
            report["models"].append({"model": name, "error_type": type(error).__name__})
            continue
        report["models"].append({"model": name, "returned_name": metadata.name,
            "input_limit": metadata.input_token_limit, "output_limit": metadata.output_token_limit,
            "supported_actions": metadata.supported_actions,
            "input_rate": input_rate, "output_rate": output_rate})
destination = root / "notes/runs/gemini-model-metadata.json"
destination.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
