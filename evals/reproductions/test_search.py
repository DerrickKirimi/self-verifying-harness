import json
from urllib.request import urlopen


def test_search_ignores_case(app_url):
    with urlopen(app_url + "/api/issues?q=login", timeout=2) as response:
        issues = json.load(response)
    assert [issue["id"] for issue in issues] == [1]
