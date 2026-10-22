"""Guide an offline reviewer through frozen M2 claims, with private resumable output."""
import argparse
import fcntl
import json
import os
from pathlib import Path
from svh.review import CONDITIONS, collect, load_packet, private_output, resume, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--condition', choices=CONDITIONS, required=True)
    parser.add_argument('--reviewer', help='Your declared identifier; software cannot authenticate human provenance')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--preview', action='store_true', help='Validate and summarize bindings without recording judgments')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    template, cases, references = load_packet(root, args.condition)
    if args.preview:
        print(json.dumps({'condition': template['condition'], 'rows': len(template['predictions']),
                          'prediction_sha256': template['prediction_sha256'],
                          'evidence_hashes_valid': True, 'judgments_recorded': 0,
                          'human_provenance_authenticated': False}, indent=2))
        return
    if not args.reviewer or not args.output:
        parser.error('--reviewer and --output are required for collecting judgments')
    path = private_output(root, args.output)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(str(path) + '.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = json.loads(path.read_text()) if path.exists() else None
        review = resume(template, previous, args.reviewer, references)
        try:
            complete = collect(review, cases, references, path)
        except (EOFError, KeyboardInterrupt):
            save(path, review); complete = False
        print('All rows collected. Run the documented scorer; no approval is inferred.' if complete
              else 'Saved completed rows; remaining decisions are still pending. Resume with the same command.')


if __name__ == '__main__':
    main()
