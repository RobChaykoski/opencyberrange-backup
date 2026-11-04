#!/usr/bin/env python3
"""RangeBox Basics - a small, safe, dependency-free training target.

Each lab selects a mode with LAB_MODE and supplies its own FLAG:

    welcome  - a welcome page and a downloadable text file
    filehunt - a small evidence archive with one flag file among decoys
    network  - a status endpoint and a token in the response headers
    browser  - a page whose HTML source contains the flag
    logs     - a synthetic web access log with a suspicious request

Nothing here reaches the internet, calls a real service, or stores state.
"""
import html
import io
import json
import os
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("LAB_MODE", "welcome")
FLAG = os.environ.get("FLAG", "OCR{rangebox_flag_not_set}")
TITLE = os.environ.get("TITLE", "RangeBox Basics")
PORT = int(os.environ.get("PORT", "8080"))

DECOY_FLAG = "OCR{d3c0y_n0t_th3_r34l_fl4g}"

STYLE = """
:root {
  --ink: #e8eef5;
  --muted: #9aa9bb;
  --panel: #152232;
  --panel-2: #1c2d40;
  --line: #30465e;
  --accent: #6ee7d8;
  --gold: #f5c76a;
  --bg: #0a121b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 231, 216, 0.10), transparent 34rem),
    radial-gradient(circle at 92% 4%, rgba(245, 199, 106, 0.08), transparent 30rem),
    var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  line-height: 1.6;
}
a { color: var(--accent); }
a:hover { text-decoration: underline; }
.wrap { width: min(900px, 92vw); margin: 0 auto; padding: 2rem 0 3rem; }
.topbar {
  display: flex; align-items: center; gap: 1rem;
  padding: 0.8rem clamp(1rem, 4vw, 3rem);
  border-bottom: 1px solid var(--line);
  background: rgba(10, 18, 27, 0.85);
  position: sticky; top: 0; z-index: 5;
}
.brand { font-weight: 800; letter-spacing: 0.14em; font-size: 0.78rem; white-space: nowrap; }
.brand span { color: var(--gold); }
.pill {
  display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
  background: var(--panel-2); border: 1px solid var(--line);
  color: var(--muted); font-size: 0.72rem; font-weight: 700;
}
h1 { font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.1; margin: 1.4rem 0 0.6rem; }
h2 { margin-top: 2rem; font-size: 1.2rem; }
p, li { color: var(--muted); }
.lede { font-size: 1.05rem; max-width: 62ch; }
.card {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: 1.2rem 1.35rem; margin: 1.2rem 0;
}
.card h2 { margin-top: 0; color: var(--ink); }
.card p:last-child { margin-bottom: 0; }
code, pre {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 0.88rem;
}
code { background: var(--panel-2); padding: 0.1rem 0.35rem; border-radius: 5px; color: var(--ink); }
pre {
  background: #07101a; border: 1px solid var(--line); border-radius: 10px;
  padding: 0.9rem 1rem; overflow-x: auto; color: #cfe3f5;
}
.button {
  display: inline-block; margin-top: 0.4rem; padding: 0.6rem 0.9rem;
  border-radius: 8px; background: var(--accent); color: #04121a;
  font-weight: 800; text-decoration: none;
}
.button:hover { text-decoration: none; filter: brightness(1.05); }
.steps li { margin-bottom: 0.45rem; }
.note { border-left: 3px solid var(--gold); padding-left: 0.8rem; }
.footer { margin-top: 2.5rem; color: #6f8297; font-size: 0.8rem; }
"""


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} - {html.escape(TITLE)}</title>
  <style>{STYLE}</style>
</head>
<body>
  <header class="topbar">
    <div class="brand">OPEN<span>CYBER</span>RANGE</div>
    <span class="pill">RangeBox basics</span>
  </header>
  <main class="wrap">
    {body}
    <p class="footer">A safe, fictional training target. Nothing here is real data.</p>
  </main>
</body>
</html>
"""


def welcome_body() -> str:
    return f"""
      <span class="pill">Start here</span>
      <h1>Welcome to your first RangeBox session</h1>
      <p class="lede">This page is a practice target. You cannot break it, and you can
      use hints at any time.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Find the training token in the welcome file, then submit it as the flag.</p>
        <a class="button" href="/welcome.txt">Open welcome.txt</a>
      </div>
      <div class="card">
        <h2>Two ways to get there</h2>
        <ol class="steps">
          <li>Open RangeBox, start the <strong>Kali</strong> desktop, and open a terminal.
              Run <code>curl http://{html.escape(os.environ.get("HOST_LABEL", "rangebox.lab"))}:8080/welcome.txt</code>.</li>
          <li>Or use the browser inside RangeBox and click the button above.</li>
        </ol>
      </div>
      <div class="card note">
        <h2>Feeling stuck?</h2>
        <p>Open the hints panel. Hints are part of the lesson, not a penalty.</p>
      </div>
    """


def filehunt_body() -> str:
    return """
      <span class="pill">File hunt</span>
      <h1>Find the one useful file</h1>
      <p class="lede">A well-meaning teammate zipped up a shared folder before a
      cleanup. Most of it is noise. One file holds the training token.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the archive, unpack it, and use <code>find</code> and
        <code>grep</code> to locate the token.</p>
        <a class="button" href="/evidence.zip">Download evidence.zip</a>
      </div>
      <div class="card">
        <h2>Suggested path</h2>
        <pre>curl -O http://files.lab:8080/evidence.zip
unzip evidence.zip
find evidence -type f
grep -R "OCR{" evidence</pre>
      </div>
      <div class="card note">
        <h2>Read before you grep</h2>
        <p>The archive contains a decoy token on purpose. The real file is the
        one described by the notes in the archive.</p>
      </div>
    """


def network_body() -> str:
    return f"""
      <span class="pill">Network basics</span>
      <h1>Ask a service how it is doing</h1>
      <p class="lede">Every web request has a request and a response. Response
      headers often carry information the page itself does not show.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Request the status endpoint and read the response headers. The
        training token is in a header named <code>X-OCR-Token</code>.</p>
        <pre>curl -i http://network.lab:8080/status.json</pre>
      </div>
      <div class="card">
        <h2>What to notice</h2>
        <ul>
          <li>The status line, such as <code>HTTP/1.1 200 OK</code></li>
          <li>The response headers, one per line</li>
          <li>The JSON body after the blank line</li>
        </ul>
      </div>
      <div class="card note">
        <h2>No terminal?</h2>
        <p>Open the lab browser and visit
        <code>http://network.lab:8080/status.json</code>. Browser developer tools
        show the same response headers under the Network tab.</p>
      </div>
    """


def browser_body() -> str:
    return f"""
      <span class="pill">Browser basics</span>
      <h1>The page is not the whole story</h1>
      <p class="lede">A web page is delivered as text. The browser turns that text
      into what you see. Viewing the source shows the parts that are easy to miss.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Open the staff notes page and view its source. The training token is in
        an HTML comment.</p>
        <a class="button" href="/staff-notes.html">Open staff-notes.html</a>
        <p style="margin-top:0.8rem">Then right-click the page and choose
        <strong>View Page Source</strong>, or press <code>Ctrl+U</code>.</p>
      </div>
      <div class="card">
        <h2>Try the terminal too</h2>
        <pre>curl http://web.lab:8080/staff-notes.html</pre>
      </div>
      <div class="card note">
        <h2>Defensive habit</h2>
        <p>Comments in source code can leak notes, internal paths, and test data.
        Remove them before publishing a page.</p>
      </div>
    """


def logs_body() -> str:
    return """
      <span class="pill">Defensive security</span>
      <h1>Read the web server log</h1>
      <p class="lede">A log is a record of what a service saw. Most lines are
      ordinary. A few can tell you that someone was probing the server.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the access log, find the suspicious requests, and recover the
        training token from the request that should never have succeeded.</p>
        <a class="button" href="/access.log">Open access.log</a>
      </div>
      <div class="card">
        <h2>Try the terminal too</h2>
        <pre>curl http://logs.lab:8080/access.log
grep " 404 " access.log
grep "OCR{" access.log</pre>
      </div>
      <div class="card note">
        <h2>Think like a defender</h2>
        <p>One source address is making repeated failed requests, then a request
        with an unusual query string. That pattern is worth explaining in a short
        incident note.</p>
      </div>
    """


def access_log() -> str:
    lines = [
        '10.0.40.15 - - [18/Mar/2026:09:01:12 +0000] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
        '10.0.40.22 - - [18/Mar/2026:09:02:45 +0000] "GET /schedule HTTP/1.1" 200 1203 "-" "Mozilla/5.0"',
        '10.0.40.31 - - [18/Mar/2026:09:04:03 +0000] "GET /health HTTP/1.1" 200 32 "-" "curl/8.5.0"',
        '10.0.40.15 - - [18/Mar/2026:09:06:20 +0000] "GET /?debug=' + DECOY_FLAG + ' HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
        '203.0.113.66 - - [18/Mar/2026:09:12:10 +0000] "GET /admin HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:13 +0000] "GET /wp-login.php HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:17 +0000] "GET /backup.sql HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:22 +0000] "GET /admin?token=' + FLAG + ' HTTP/1.1" 200 512 "-" "sqlmap/1.8"',
        '10.0.40.22 - - [18/Mar/2026:09:14:51 +0000] "GET /schedule HTTP/1.1" 200 1203 "-" "Mozilla/5.0"',
        '10.0.40.31 - - [18/Mar/2026:09:16:08 +0000] "GET /health HTTP/1.1" 200 32 "-" "curl/8.5.0"',
        '10.0.40.15 - - [18/Mar/2026:09:18:33 +0000] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
    ]
    return "\n".join(lines) + "\n"


def evidence_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        files = {
            "evidence/README.txt": (
                "Shared folder export\n"
                "====================\n\n"
                "This archive was created during a classroom cleanup.\n"
                "The useful training token is in archive/old/flag.txt.\n"
                "The other files are decoys kept for practice.\n"
            ),
            "evidence/notes/team.txt": "Team: RangeBox practice group\n",
            "evidence/notes/schedule.txt": "Monday: accounts\nTuesday: files\n",
            "evidence/archive/old/flag.txt": f"Training token: {FLAG}\n",
            "evidence/archive/old/notes.txt": "Old notes. Nothing important here.\n",
            "evidence/archive/old/decoy.txt": f"Decoy token: {DECOY_FLAG}\n",
            "evidence/photos/readme.txt": "No photos in this training archive.\n",
        }
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class Handler(BaseHTTPRequestHandler):
    server_version = "RangeBoxBasics/1.0"

    def log_message(self, format, *args):
        return

    def _send(self, status, body, content_type="text/html; charset=utf-8", extra_headers=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if MODE == "network":
            self.send_header("X-OCR-Token", FLAG)
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(data)

    def do_HEAD(self):
        self._head_only = True
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if MODE == "welcome":
            if path in ("/", "/index.html"):
                body = page("Welcome", welcome_body())
            elif path == "/welcome.txt":
                self._send(200, f"RangeBox first steps\n\nTraining token: {FLAG}\n", "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "filehunt":
            if path in ("/", "/index.html"):
                body = page("File hunt", filehunt_body())
            elif path == "/evidence.zip":
                self._send(200, evidence_zip(), "application/zip", {"Content-Disposition": 'attachment; filename="evidence.zip"'})
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "network":
            if path in ("/", "/index.html"):
                body = page("Network basics", network_body())
            elif path == "/status.json":
                payload = {
                    "service": "rangebox-basics",
                    "status": "ok",
                    "lesson": "Read the X-OCR-Token response header.",
                }
                self._send(200, json.dumps(payload), "application/json")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "logs":
            if path in ("/", "/index.html"):
                body = page("Log detective", logs_body())
            elif path == "/access.log":
                self._send(200, access_log(), "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "browser":
            if path in ("/", "/index.html"):
                body = page("Browser basics", browser_body())
            elif path == "/staff-notes.html":
                body = page(
                    "Staff notes",
                    f"<h1>Staff notes</h1><p>This page is mostly empty on purpose.</p>"
                    f"<!-- Training token: {FLAG} -->",
                )
            elif path == "/robots.txt":
                self._send(200, "User-agent: *\nDisallow: /staff-notes.html\n", "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        else:
            self._send(500, page("Configuration error", "<h1>Unknown LAB_MODE</h1>"))
            return

        self._send(200, body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
