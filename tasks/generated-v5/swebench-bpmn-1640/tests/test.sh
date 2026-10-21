#!/bin/bash
set -eu
mkdir -p /logs/verifier
printf '{"reward":0}\n' > /logs/verifier/reward.json
python3 -I /tests/verify.py
