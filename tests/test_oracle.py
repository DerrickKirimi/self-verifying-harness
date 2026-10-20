import pytest

from svh.oracle import classify, contained, wilson


@pytest.mark.parametrize("code,xml,status", [
    (0, '<testsuite><testcase/></testsuite>', "pass"),
    (1, '<testsuite><testcase><failure message="assert [] == [1]"/></testcase></testsuite>', "assertion_failure"),
    (1, '<testsuite><testcase><failure message="AssertionError: assert a == b"/></testcase></testsuite>', "assertion_failure"),
    (1, '<testsuite><testcase><failure message="ConnectionError"/></testcase></testsuite>', "error"),
    (1, '<testsuite><testcase><error message="setup failed"/></testcase></testsuite>', "error"),
    (2, '<testsuite><testcase><error message="import error"/></testcase></testsuite>', "error"),
    (0, '<testsuite><testcase><skipped/></testcase></testsuite>', "error"),
    (0, '<testsuite/>', "error"),
    (0, '<testsuite><testcase/><testcase/></testsuite>', "error"),
    (0, 'broken XML', "error"),
    (0, None, "error"),
])
def test_errors_cannot_verify_claims(code, xml, status):
    assert classify({"exit_code": code, "junit": xml}) == status


def test_path_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        contained(tmp_path, "../outside")


def test_small_sample_uncertainty():
    low, high = wilson(3, 3)
    assert 0.43 < low < 0.44
    assert high == 1.0
    assert wilson(0, 0) == [0.0, 1.0]
