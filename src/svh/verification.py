"""Prospective M3 evidence scoring; never trust an agent's verification verdict."""
import hashlib
from svh.oracle import wilson


def digest(data):
    return hashlib.sha256(data).hexdigest()


def browser_verdict(report, *, assertion_failure=False):
    """Require a completed runner observation, not scraped generated console text."""
    if (report.get('exit_code') is None or report.get('timed_out')
            or not report.get('complete') or report.get('errors')
            or not report.get('browser') or report.get('disconnected')
            or report.get('total', 0) < 1 or report.get('skipped') != 0
            or len(report.get('results', [])) != report['total']):
        return False
    results = report['results']
    if assertion_failure:
        failures = [r for r in results if r.get('success') is False]
        return (report['exit_code'] != 0 and bool(failures)
            and all(any('AssertionError' in log for log in r.get('log', [])) for r in failures))
    return report['exit_code'] == 0 and all(r.get('success') is True for r in results)


def verified_check(pre, post):
    return (pre.get('check_sha256') == post.get('check_sha256')
        and bool(pre.get('check_sha256')) and pre.get('image') == post.get('image')
        and pre.get('base_commit') == post.get('base_commit')
        and bool(pre.get('image')) and bool(pre.get('base_commit'))
        and pre.get('runner_sha256') == post.get('runner_sha256') and bool(pre.get('runner_sha256'))
        and pre.get('source_archive_sha256') == post.get('source_archive_sha256')
        and pre.get('source_is_base') is True and post.get('source_is_base') is False
        and bool(post.get('source_files_sha256'))
        and browser_verdict(pre, assertion_failure=True) and browser_verdict(post)
        and pre['total'] == post['total']
        and [r['name'] for r in pre['results']] == [r['name'] for r in post['results']])


def score(attempts, rubric, expected_ids):
    if len(attempts) != len(expected_ids) or {a['id'] for a in attempts} != set(expected_ids):
        raise ValueError('Keep all frozen cases, including abstentions and exhausted budgets')
    def aligned(c):
        review=c.get('alignment_review', {})
        return review.get('aligned') is True and review.get('check_sha256') == c.get('pre',{}).get('check_sha256')
    valid = sum(any(aligned(c) and verified_check(c.get('pre', {}), c.get('post', {})) for c in a.get('candidates', [])) for a in attempts)
    repaired = sum(any(aligned(c) and verified_check(c.get('pre', {}), c.get('post', {})) and c.get('native_regressions_passed') is True
                       for c in a.get('candidates', [])) for a in attempts)
    n=len(attempts)
    attempted=sum(a.get('status') != 'not_attempted' for a in attempts)
    return {'artifacts': n, 'attempted_artifacts': attempted, 'valid_reproductions': {'successes': valid, 'n': n, 'wilson95': wilson(valid,n)},
            'full_generated_repairs': {'successes': repaired, 'n': n, 'wilson95': wilson(repaired,n)},
            'generated_verification_gate_passed': attempted == n and n >= rubric['minimum_artifacts'] and wilson(valid,n)[0] >= rubric['valid_reproduction_wilson_lower'] and repaired >= rubric['minimum_full_generated_repairs']}
