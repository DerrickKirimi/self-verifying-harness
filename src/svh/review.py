"""Offline collection of declared reviewer decisions; no model or human authentication."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

FIELDS = ('gold_claim_id', 'symptom_match', 'expected_match', 'source_support', 'reason')
CONDITIONS = {
    'media': ('notes/runs/m2-refined-media.json', 'evals/m2-human-review-template.json'),
    'issue-only': ('notes/runs/m2-refined-issue-only.json', 'evals/m2-human-issue-only-template.json'),
}


def load_packet(root, condition):
    from svh.corpus import load_frozen_corpus
    manifest, annotations = load_frozen_corpus(root, root / 'evals/frozen-m0.json')
    prediction_path, template_path = CONDITIONS[condition]
    data = (root / prediction_path).read_bytes()
    predictions = json.loads(data)
    template = json.loads((root / template_path).read_text())
    if (template['prediction_sha256'] != sha256(data).hexdigest()
            or template['condition'] != predictions['condition']
            or predictions['corpus_sha256'] != manifest['corpus_sha256']):
        raise ValueError('Review packet belongs to different frozen predictions')
    cases = {case['id']: case for case in predictions['cases']}
    references = {case['id']: case for case in annotations}
    expected = {(case['id'], pred['id']) for case in predictions['cases'] for pred in case['predictions']}
    keys = [(row['recording_id'], row['prediction_id']) for row in template['predictions']]
    if len(set(keys)) != len(keys) or set(keys) != expected:
        raise ValueError('Review packet must cover every frozen prediction exactly once')
    for row in template['predictions']:
        case = cases[row['recording_id']]
        annotation = references[row['recording_id']]
        media = root / annotation['media']['path']
        if sha256(media.read_bytes()).hexdigest() != annotation['media']['sha256']:
            raise ValueError('Review recording changed')
        source = row.get('review_source')
        if source and (source['response_sha256'] != case['response_sha256']
                or source['media_sha256'] != annotation['media']['sha256']
                or sha256((root / source['path']).read_bytes()).hexdigest() != source['sha256']):
            raise ValueError('Review source evidence changed')
    return template, cases, references


def decision_complete(row, reference):
    if not all(type(row.get(key)) is bool for key in FIELDS[1:4]):
        return False
    if not isinstance(row.get('reason'), str) or not row['reason'].strip():
        return False
    matches = row['symptom_match'] and row['expected_match']
    return (row['gold_claim_id'] in {c['id'] for c in reference['claims']} if matches
            else row['gold_claim_id'] is None)


def resume(template, previous, reviewer, references):
    if not isinstance(reviewer, str) or not reviewer.strip() or reviewer.upper().startswith('UNREVIEWED'):
        raise ValueError('Supply your reviewer identifier; it is declared, not authenticated')
    result = deepcopy(template)
    result['scorer'] = reviewer
    if previous is None:
        return result
    if previous == template:
        return result  # A manually copied, entirely blank template is safe to start.
    if previous.get('scorer') != reviewer or len(previous.get('predictions', [])) != len(result['predictions']):
        raise ValueError('Existing review belongs to a different reviewer or packet')
    for target, prior in zip(result['predictions'], previous['predictions']):
        if any(prior.get(key) != target.get(key) for key in ('recording_id', 'prediction_id')):
            raise ValueError('Existing review order or prediction changed')
        pending = all(prior.get(key) == target.get(key) for key in FIELDS)
        if not pending and not decision_complete(prior, references[target['recording_id']]):
            raise ValueError('Existing review has a partial or invalid decision')
        for key in FIELDS:
            target[key] = prior[key]
    if result != previous:
        raise ValueError('Immutable review bindings changed')
    return result


def private_output(root, path):
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    if path.is_symlink() or not path.resolve().is_relative_to((root / 'data/runtime').resolve()):
        raise ValueError('Keep reviewer identities and judgments in an ignored data/runtime file')
    if path.exists() and (not path.is_file() or path.stat().st_mode & 0o077):
        raise ValueError('Existing review must be an owner-only regular file')
    return path


def save(path, review):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix='.review-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(review, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def collect(review, cases, references, path, *, ask=input, show=print):
    """Save only complete, explicitly confirmed rows; quit leaves others undecided."""
    for row in review['predictions']:
        reference = references[row['recording_id']]
        if decision_complete(row, reference):
            continue
        prediction = next(p for p in cases[row['recording_id']]['predictions'] if p['id'] == row['prediction_id'])
        show(json.dumps({'recording': reference['media']['path'], 'prediction': prediction,
                        'reference_claims': [{k: c[k] for k in ('id', 'text', 't_start_s', 't_end_s')}
                                             for c in reference['claims']],
                        'contact_sheet': row.get('review_source', {}).get('path')}, indent=2))
        show('Watch the full source. No previous AI decisions are shown. Type q to save and stop.')
        proposed = deepcopy(row)
        for key, prompt in [('symptom_match', 'Does the symptom match the recording/reference?'),
                            ('expected_match', 'Does expected behavior match without inventing policy?'),
                            ('source_support', 'Does the prediction cite supporting recording evidence? Issue-only input has no recording.')]:
            while True:
                value = ask(prompt + ' [y/n/q] ').strip().lower()
                if value == 'q':
                    save(path, review); return False
                if value in ('y', 'n'):
                    proposed[key] = value == 'y'; break
        proposed['gold_claim_id'] = None
        if proposed['symptom_match'] and proposed['expected_match']:
            while proposed['gold_claim_id'] not in {c['id'] for c in reference['claims']}:
                value = ask('Matching reference claim ID (q to stop): ').strip()
                if value == 'q': save(path, review); return False
                proposed['gold_claim_id'] = value
        while not proposed['reason'].strip():
            value = ask('Your reason (q to stop): ').strip()
            if value == 'q': save(path, review); return False
            proposed['reason'] = value
        if ask('Save this decision? [y/N] ').strip().lower() != 'y':
            save(path, review); return False
        row.update(proposed)
        save(path, review)
    return True
