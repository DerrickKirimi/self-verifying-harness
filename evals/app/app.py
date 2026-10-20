"""Owner-controlled, deterministic issue board for recording M0 walkthroughs.

Revision 426a532 intentionally contains three bugs. Git history is the fixture;
there is no runtime switch that can make a reproduction pass.
"""

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit


ISSUES = [
    {"id": 1, "title": "Login fails after reset", "status": "open", "priority": "high"},
    {"id": 2, "title": "Export is slow", "status": "closed", "priority": "low"},
    {"id": 3, "title": "Keyboard navigation", "status": "open", "priority": "medium"},
]


def select_issues(query="", status="all", sort="id"):
    issues = [issue for issue in ISSUES if query.casefold() in issue["title"].casefold()]
    if status != "all":
        issues = [issue for issue in issues if issue["status"] == status]
    if sort == "priority":
        order = {"high": 0, "medium": 1, "low": 2}
        issues.sort(key=lambda issue: order[issue["priority"]])
    return issues


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path not in ("/", "/api/issues"):
            self.send_error(404)
            return
        params = parse_qs(url.query)
        query = params.get("q", [""])[0]
        status = params.get("status", ["all"])[0]
        sort = params.get("sort", ["id"])[0]
        issues = select_issues(query, status, sort)
        if url.path == "/api/issues":
            body = json.dumps(issues).encode()
            content_type = "application/json"
        else:
            links = " ".join(
                f'<a href="/?{html.escape(urlencode(values))}">{label}</a>'
                for label, values in [
                    ("All", {}), ("Closed", {"status": "closed"}),
                    ("Priority", {"sort": "priority"}),
                ]
            )
            rows = "".join(
                f'<tr><td>{issue["id"]}</td><td>{html.escape(issue["title"])}</td>'
                f'<td>{issue["status"]}</td><td>{issue["priority"]}</td></tr>'
                for issue in issues
            )
            body = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>M0 issue board</title><style>
body {{font:18px system-ui;max-width:900px;margin:60px auto;background:#f6f7fb;color:#14253b}}
table {{width:100%;margin-top:24px;border-collapse:collapse;background:white}}
td,th {{padding:16px;text-align:left;border-bottom:1px solid #ddd}}
input,button,a {{font:inherit;padding:8px}} a {{display:inline-block}}
</style><h1>M0 issue board</h1><p>Local fixture · planted bugs · fictional data</p>
<form><label>Search titles <input name="q" value="{html.escape(query, quote=True)}"></label>
<button>Search</button></form><nav>{links}</nav>
<p>{len(issues)} issues</p><table><thead><tr><th>ID</th><th>Title</th><th>Status</th>
<th>Priority</th></tr></thead><tbody>{rows}</tbody></table></html>'''.encode()
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
