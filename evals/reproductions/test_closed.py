import json
from urllib.request import urlopen


def test_closed_filter_excludes_open(app_url):
    with urlopen(app_url + "/api/issues?status=closed", timeout=2) as response:
        issues = json.load(response)
    assert [issue["id"] for issue in issues] == [2]
