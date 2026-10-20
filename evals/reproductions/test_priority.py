import json
from urllib.request import urlopen


def test_priority_is_high_medium_low(app_url):
    with urlopen(app_url + "/api/issues?sort=priority", timeout=2) as response:
        issues = json.load(response)
    assert [issue["priority"] for issue in issues] == ["high", "medium", "low"]
