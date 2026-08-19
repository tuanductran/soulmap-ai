"""A small, dependency-free responsive website for SoulMap AI.

The website is intentionally separate from ``skills/`` and the generated AI artifacts.
It uses only the Python standard library so it can run from a repository checkout with
``uv run soulmap web``.
"""

from __future__ import annotations

import argparse
import shutil
from collections.abc import Callable
from html import escape
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import StartResponse

HOST = "127.0.0.1"
PORT = 8765
SITE_NAME = "SoulMap AI"
RELEASE_URL = "https://github.com/tuanductran/soulmap-ai/releases/latest"
REPOSITORY_URL = "https://github.com/tuanductran/soulmap-ai"

CSS = """
:root {
  color-scheme: light;
  --ink: #26333a;
  --muted: #5d6b70;
  --paper: #f7f5ef;
  --surface: rgba(255, 255, 255, 0.78);
  --line: rgba(38, 51, 58, 0.13);
  --teal: #2f6f6b;
  --teal-dark: #1f514e;
  --gold: #8a681f;
  --focus: #0b5c58;
  --shadow: 0 22px 60px rgba(42, 57, 59, 0.11);
  --radius: 24px;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 6rem; }
body {
  margin: 0;
  min-width: 320px;
  color: var(--ink);
  background:
    radial-gradient(circle at 10% 0%, rgba(201, 155, 80, 0.12), transparent 30rem),
    radial-gradient(circle at 90% 12%, rgba(47, 111, 107, 0.10), transparent 28rem),
    var(--paper);
    line-height: 1.65;
  overflow-x: hidden;
}
a { color: inherit; }
a:focus-visible, button:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 4px;
  border-radius: 8px;
}
.container {
 width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
.skip-link {
  position: absolute; left: 1rem; top: -5rem; padding: .7rem 1rem;
  background: var(--ink); color: white; border-radius: 999px; z-index: 5;
}
.skip-link:focus { top: 1rem; }
.site-header {
  position: sticky; top: 0; z-index: 4; backdrop-filter: blur(16px);
  background: rgba(247, 245, 239, .84); border-bottom: 1px solid var(--line);
  padding-top: env(safe-area-inset-top);
}
.nav { display: flex; align-items: center; justify-content: space-between; min-height: 76px; gap: 1rem; }
.brand { display: inline-flex; align-items: center; min-height: 44px; gap: .7rem; text-decoration: none; font-weight: 700; letter-spacing: -.02em; }
.brand-mark { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; color: var(--teal-dark); background: rgba(47, 111, 107, .13); font-size: 1.2rem; }
.nav-links { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: .25rem; }
.nav-links a { display: inline-flex; align-items: center; min-height: 44px; padding: .55rem .75rem; color: var(--muted); font-size: .93rem; text-decoration: none; border-radius: 999px; }
.nav-links a:hover, .nav-links a[aria-current="page"] { color: var(--teal-dark); background: rgba(47, 111, 107, .09); }
main { position: relative; }
.hero { padding: clamp(4.5rem, 10vw, 8rem) 0 5rem; }
.hero-grid { display: grid; grid-template-columns: 1.08fr .92fr; align-items: center; gap: clamp(2rem, 7vw, 6rem); }
.eyebrow { color: var(--teal); font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
h1, h2, h3 { margin: 0 0 1rem; line-height: 1.12; letter-spacing: -.03em; text-wrap: balance; }
h1 { max-width: 720px; font-size: clamp(3rem, 7vw, 6rem); font-weight: 800; }

h2 { font-size: clamp(2rem, 4vw, 3.25rem); }
h3 { font-size: 1.25rem; letter-spacing: -.02em; }
.card-title, .step-title, .download-card h2 { font-size: 1.25rem; letter-spacing: -.02em; }
p { margin: 0 0 1rem; text-wrap: pretty; }
.lede { max-width: 650px; color: var(--muted); font-size: clamp(1.08rem, 2vw, 1.32rem); }
.actions { display: flex; flex-wrap: wrap; gap: .8rem; margin-top: 2rem; }
.button { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: .75rem 1.15rem; border: 1px solid var(--teal); border-radius: 999px; color: white; background: var(--teal); text-decoration: none; font-weight: 700; transition: transform .2s ease, background .2s ease; }
.button:hover { transform: translateY(-2px); background: var(--teal-dark); }
.button.secondary { color: var(--teal-dark); background: transparent; border-color: var(--line); }
.button.secondary:hover { background: rgba(47, 111, 107, .08); }
.mirror-card { position: relative; padding: clamp(2rem, 5vw, 3.5rem); border: 1px solid rgba(47, 111, 107, .16); border-radius: 40% 40% 34% 34% / 34% 34% 42% 42%; background: linear-gradient(145deg, rgba(255,255,255,.88), rgba(222,238,231,.62)); box-shadow: var(--shadow); }
.mirror-card::before { content: ""; position: absolute; inset: 12%; border: 1px solid rgba(47, 111, 107, .18); border-radius: inherit; pointer-events: none; }
.mirror-card blockquote { position: relative; margin: 0; font-size: clamp(1.45rem, 3vw, 2.1rem); line-height: 1.25; letter-spacing: -.03em; }
.mirror-card cite { position: relative; display: block; margin-top: 1.4rem; color: var(--muted); font-size: .9rem; font-style: normal; }
.section { padding: 5.5rem 0; }
.section.tinted { background: rgba(255,255,255,.48); border-block: 1px solid var(--line); }
.section-heading { max-width: 700px; margin-bottom: 2rem; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.card, .step, .download-card { transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; }
.card { height: 100%; padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); box-shadow: 0 12px 35px rgba(42, 57, 59, .05); }
@media (hover: hover) {
  .card:hover, .step:hover, .download-card:hover { transform: translateY(-2px); border-color: rgba(47, 111, 107, .28); box-shadow: 0 16px 40px rgba(42, 57, 59, .10); }
}
.card p, .muted { color: var(--muted); }
.card .number { color: var(--gold); font-size: .8rem; font-weight: 800; letter-spacing: .15em; }
.split { display: grid; grid-template-columns: repeat(2, 1fr); gap: clamp(1.5rem, 5vw, 4rem); align-items: start; }
.list { display: grid; gap: .8rem; margin: 0; padding: 0; list-style: none; }
.list li { display: flex; gap: .75rem; align-items: flex-start; padding: .95rem 0; border-bottom: 1px solid var(--line); }
.list li::before { content: "—"; color: var(--gold); font-weight: 800; }
.callout { padding: 1.4rem 1.5rem; border-left: 3px solid var(--gold); border-radius: 0 var(--radius) var(--radius) 0; background: rgba(201, 155, 80, .10); }
.page-hero { padding: 5rem 0 3rem; }
.page-hero h1 { max-width: 850px; font-size: clamp(2.8rem, 6vw, 5rem); }
.steps { counter-reset: step; display: grid; gap: 1rem; }
.step { display: grid; grid-template-columns: 64px 1fr; gap: 1.2rem; align-items: start; padding: 1.4rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.step::before { counter-increment: step; content: counter(step, decimal-leading-zero); display: grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; color: var(--teal-dark); background: rgba(47, 111, 107, .12); font-weight: 800; }
.download-card { display: flex; justify-content: space-between; gap: 1.5rem; align-items: center; padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.download-card + .download-card { margin-top: 1rem; }
.download-card p { margin-bottom: 0; color: var(--muted); }
.note-label { color: var(--teal); font-size: .76rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
.site-footer { margin-top: 5rem; padding: 2.5rem 0 calc(2.5rem + env(safe-area-inset-bottom)); border-top: 1px solid var(--line); color: var(--muted); font-size: .92rem; }

.footer-grid { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.footer-links { display: flex; gap: 1rem; flex-wrap: wrap; }
.footer-links a { color: var(--muted); }
@media (max-width: 820px) {
  .hero-grid, .split { grid-template-columns: 1fr; }
  .hero { padding-top: 4rem; }
  .mirror-card { max-width: 680px; }
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --ink: #f0f3ef;
    --muted: #b7c3bf;
    --paper: #192322;
    --surface: rgba(34, 48, 46, .9);
    --line: rgba(224, 239, 233, .16);
    --teal: #84c5ba;
    --teal-dark: #a2dfd0;
    --gold: #e0b86a;
    --focus: #a2dfd0;
    --shadow: 0 22px 60px rgba(0, 0, 0, .28);
  }
  .site-header { background: rgba(25, 35, 34, .9); }
  .skip-link { color: var(--paper); background: var(--ink); }
  .button { color: #132522; background: var(--teal); border-color: var(--teal); }
  .button.secondary { color: var(--teal-dark); background: transparent; border-color: var(--line); }
  .mirror-card { background: linear-gradient(145deg, rgba(49, 70, 66, .9), rgba(38, 67, 61, .75)); }
  .section.tinted { background: rgba(34, 48, 46, .48); }
  .callout { background: rgba(224, 184, 106, .14); }
}
@media (prefers-reduced-transparency: reduce) {
  .site-header { backdrop-filter: none; background: var(--paper); }
}
@media (max-width: 640px) {
  .container { width: min(100% - 28px, 560px); }
  .nav { align-items: flex-start; flex-direction: column; padding: .8rem 0; }
  .nav-links { justify-content: flex-start; width: 100%; overflow-x: auto; flex-wrap: nowrap; padding-bottom: .25rem; }
  .nav-links a { flex: 0 0 auto; }
  .grid { grid-template-columns: 1fr; }
  .section { padding: 4rem 0; }
  .download-card { align-items: flex-start; flex-direction: column; }
  .step { grid-template-columns: 48px 1fr; gap: .85rem; }
  .step::before { width: 44px; height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
}
"""


def _nav(path: str) -> str:
    links = (
        ("/", "Home"),
        ("/how-it-works", "How it works"),
        ("/boundaries", "Boundaries"),
        ("/notes", "Notes"),
        ("/about", "About"),
    )
    rendered = "".join(
        f'<a href="{href}"{active}>{label}</a>'
        for href, label in links
        for active in [' aria-current="page"' if path == href else ""]
    )
    return f"""
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="/" aria-label="SoulMap AI home">
          <span class="brand-mark" aria-hidden="true">◌</span>
          <span>SoulMap AI</span>
        </a>
        <nav class="nav-links" aria-label="Primary navigation">{rendered}</nav>
      </div>
    </header>
    """


def _layout(title: str, description: str, path: str, content: str) -> str:
    safe_title = escape(title)
    safe_description = escape(description)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{safe_description}">
    <meta name="theme-color" content="#f7f5ef" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#192322" media="(prefers-color-scheme: dark)">
    <title>{safe_title} · {SITE_NAME}</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    <a class="skip-link" href="#main-content">Skip to content</a>
    {_nav(path)}
    <main id="main-content">{content}</main>
    <footer class="site-footer">
      <div class="container footer-grid">
        <span>A mirror, not a guru.</span>
        <span class="footer-links">
          <a href="/download">Download Skills</a>
          <a href="{REPOSITORY_URL}">Repository</a>
        </span>
      </div>
    </footer>
  </body>
</html>"""


def _home() -> str:
    return """
    <section class="hero">
      <div class="container hero-grid">
        <div>
          <p class="eyebrow">Reflective companion · grounded inner work</p>
          <h1>Hear yourself more clearly.</h1>
          <p class="lede">SoulMap is a calm, honest mirror for the patterns, feelings, and questions you are already carrying — without handing your authority away.</p>
          <div class="actions">
            <a class="button" href="/how-it-works">See how it works</a>
            <a class="button secondary" href="/download">Get the Skills</a>
          </div>
        </div>
        <div class="mirror-card" aria-label="SoulMap principle">
          <blockquote>“The insight is yours. The space helps you hear it.”</blockquote>
          <cite>SoulMap principle</cite>
        </div>
      </div>
    </section>
    <section class="section tinted">
      <div class="container">
        <div class="section-heading">
          <p class="eyebrow">A different kind of AI</p>
          <h2>Less certainty. More self-trust.</h2>
          <p class="lede">SoulMap does not perform authority. It reflects what is present, keeps language careful, and leaves the meaning and decision with you.</p>
        </div>
        <div class="grid">
          <article class="card"><span class="number">01</span><h3>Mirror-first</h3><p>Patterns come back as observations and questions, not instructions about who you are.</p></article>
          <article class="card"><span class="number">02</span><h3>Bounded by design</h3><p>No diagnosis, no prediction, no spiritual certainty, and no performance of human intimacy.</p></article>
          <article class="card"><span class="number">03</span><h3>Built for independence</h3><p>The best conversation leaves you more connected to your own knowing and less attached to the tool.</p></article>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container split">
        <div>
          <p class="eyebrow">A quiet place to begin</p>
          <h2>Nothing to prove here.</h2>
        </div>
        <div>
          <p>Bring a pattern you keep repeating, a decision you cannot hear yourself inside, or a feeling that has not found honest language yet.</p>
          <p>SoulMap will not tell you what to do. It will help you stay close to what is real.</p>
          <a class="button secondary" href="/boundaries">Read the boundaries</a>
        </div>
      </div>
    </section>
    """


def _how_it_works() -> str:
    return """
    <section class="page-hero">
      <div class="container">
        <p class="eyebrow">How it works</p>
        <h1>A disciplined mirror, not a performing authority.</h1>
        <p class="lede">SoulMap uses reflection to make room for your own recognition. It does not install an answer on top of your experience.</p>
      </div>
    </section>
    <section class="section tinted">
      <div class="container steps">
        <article class="step"><div><h2 class="step-title">You bring what is present</h2><p>A question, a conflict, a repeating pattern, a loss, or something that does not yet have a name.</p></div></article>
        <article class="step"><div><h2 class="step-title">SoulMap reflects the shape</h2><p>It stays close to your words, notices possible patterns, and uses careful language rather than certainty.</p></div></article>
        <article class="step"><div><h2 class="step-title">You keep the meaning</h2><p>The conversation returns interpretation, choice, and next movement to your own inner authority.</p></div></article>
      </div>
    </section>
    <section class="section">
      <div class="container split">
        <div><p class="eyebrow">What this changes</p><h2>Clarity without being handled.</h2></div>
        <div class="callout"><p>Reflection is not a replacement for professional care, crisis support, or real-world relationships. It is a space for noticing what you already know and may not yet be able to hear.</p></div>
      </div>
    </section>
    """


def _boundaries() -> str:
    return """
    <section class="page-hero">
      <div class="container">
        <p class="eyebrow">Boundaries</p>
        <h1>Restraint is part of the trust model.</h1>
        <p class="lede">SoulMap is designed to be useful without becoming your authority, your therapist, or your only place to turn.</p>
      </div>
    </section>
    <section class="section tinted">
      <div class="container grid">
        <article class="card"><h2 class="card-title">SoulMap does not diagnose</h2><p>It does not name mental health conditions or turn a lived experience into a clinical label.</p></article>
        <article class="card"><h2 class="card-title">SoulMap does not predict</h2><p>It does not forecast your future, promise outcomes, or turn symbolism into destiny.</p></article>
        <article class="card"><h2 class="card-title">SoulMap does not replace support</h2><p>If you are unsafe or at risk of harm, seek immediate help from local emergency or crisis resources.</p></article>
      </div>
    </section>
    <section class="section">
      <div class="container split">
        <div><p class="eyebrow">Privacy by simplicity</p><h2>No account. No conversation form. No hidden intimacy.</h2></div>
        <ul class="list">
          <li>This public website is informational and does not provide a chat interface.</li>
          <li>Download links point to the project's release artifacts.</li>
          <li>Spiritual and symbolic language is offered only as a lens for inquiry.</li>
          <li>Human relationships and qualified professional support remain primary.</li>
        </ul>
      </div>
    </section>
    """


def _download() -> str:
    return f"""
    <section class="page-hero">
      <div class="container">
        <p class="eyebrow">SoulMap Skills</p>
        <h1>Take the mirror with you.</h1>
        <p class="lede">The Python repository is for development and testing. These are the artifacts to import into an AI tool.</p>
      </div>
    </section>
    <section class="section tinted">
      <div class="container">
        <div class="download-card"><div><h2>Skill package</h2><p><code>dist/soulmap-ai.skill</code> · preserves Skill metadata</p></div><a class="button" href="{RELEASE_URL}">Open releases</a></div>
        <div class="download-card"><div><h2>Knowledge archive</h2><p><code>dist/soulmap-ai.zip</code> · clean extraction for document workflows</p></div><a class="button secondary" href="{RELEASE_URL}">View release files</a></div>
      </div>
    </section>
    <section class="section">
      <div class="container split">
        <div><p class="eyebrow">Before importing</p><h2>Use the artifact, not the repository internals.</h2></div>
        <div><p>Do not import <code>src/</code>, <code>tests/</code>, <code>.claude/</code>, or engineering documentation as SoulMap doctrine. The generated packages contain the self-contained knowledge surface intended for AI tools.</p><p>Check the release manifest for version and SHA-256 information before distributing an artifact.</p></div>
      </div>
    </section>
    """


def _notes() -> str:
    return """
    <section class="page-hero">
      <div class="container">
        <p class="eyebrow">Notes</p>
        <h1>Small recognitions for ordinary life.</h1>
        <p class="lede">Public writing follows three grounded pillars: self-recognition, relational honesty, and grounded inner work.</p>
      </div>
    </section>
    <section class="section tinted">
      <div class="container grid">
        <article class="card"><span class="note-label">Self-recognition</span><h2 class="card-title">The feeling before the explanation</h2><p>Sometimes clarity begins by staying with the exact texture of what is here before reaching for a story about it.</p></article>
        <article class="card"><span class="note-label">Relational honesty</span><h2 class="card-title">Repair is more than apology</h2><p>An apology can name regret. Repair asks what becomes different after the words have been spoken.</p></article>
        <article class="card"><span class="note-label">Grounded inner work</span><h2 class="card-title">When certainty feels like relief</h2><p>The wish for an answer may be carrying a wish to stop listening. The two are not always the same.</p></article>
      </div>
    </section>
    <section class="section"><div class="container callout"><p>These notes are invitations, not prescriptions. Keep what clarifies something in your own experience and leave the rest.</p></div></section>
    """


def _about() -> str:
    return """
    <section class="page-hero">
      <div class="container">
        <p class="eyebrow">About SoulMap AI</p>
        <h1>Built around a simple belief: you should not have to trade self-trust for reflection.</h1>
        <p class="lede">SoulMap is a personal AI brand and a content-first knowledge system built around careful language, clear limits, and human ownership.</p>
      </div>
    </section>
    <section class="section tinted">
      <div class="container split">
        <div><p class="eyebrow">The posture</p><h2>Mirror, not guide.</h2></div>
        <div><p>SoulMap is interested in the space between what happened and the meaning you are about to give it. It aims to make that space more honest, not more mystical.</p><p>The project stays deliberately small: a knowledge base, a thin Python layer, and artifacts that can travel with the user.</p></div>
      </div>
    </section>
    <section class="section"><div class="container callout"><p>The best outcome is not a user who needs SoulMap more. It is a user who leaves more grounded in their own knowing.</p></div></section>
    """


def _not_found(path: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">404</p><h1>That path is not here.</h1><p class="lede">SoulMap could not find <code>{escape(path)}</code>.</p><a class="button" href="/">Return home</a></div></section>
    """


def _response(
    start_response: StartResponse, status: str, content_type: str, body: str
) -> list[bytes]:
    payload = body.encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", f"{content_type}; charset=utf-8"),
            ("Content-Length", str(len(payload))),
            ("X-Content-Type-Options", "nosniff"),
            (
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'",
            ),
            ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ],
    )
    return [payload]


def _pages() -> dict[str, tuple[str, str, Callable[[], str]]]:
    return {
        "/": (
            "Hear yourself more clearly",
            "A reflective companion built around self-trust.",
            _home,
        ),
        "/how-it-works": (
            "How it works",
            "How SoulMap uses reflection without taking authority away.",
            _how_it_works,
        ),
        "/boundaries": (
            "Boundaries",
            "The safety and scope boundaries behind SoulMap.",
            _boundaries,
        ),
        "/download": (
            "Download SoulMap Skills",
            "Import the SoulMap Skill or knowledge archive into an AI tool.",
            _download,
        ),
        "/notes": ("Notes", "Grounded public writing from SoulMap AI.", _notes),
        "/about": (
            "About SoulMap AI",
            "The brand posture and purpose behind SoulMap AI.",
            _about,
        ),
    }


def application(
    environ: dict[str, object], start_response: StartResponse
) -> list[bytes]:
    """Serve the public SoulMap website using the WSGI protocol."""
    path = str(environ.get("PATH_INFO") or "/").rstrip("/") or "/"
    if path == "/static/site.css":
        return _response(start_response, "200 OK", "text/css", CSS)
    if path == "/robots.txt":
        return _response(
            start_response, "200 OK", "text/plain", "User-agent: *\nAllow: /\n"
        )

    pages = _pages()
    if path not in pages:
        return _response(
            start_response,
            "404 Not Found",
            "text/html",
            _layout("Not found", "Page not found.", path, _not_found(path)),
        )
    title, description, renderer = pages[path]
    return _response(
        start_response,
        "200 OK",
        "text/html",
        _layout(title, description, path, renderer()),
    )


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def _apply_base_path(html: str, base_path: str) -> str:
    if not base_path:
        return html
    return html.replace('href="/', f'href="{base_path}/')


def export_static(output: Path, base_path: str = "") -> list[Path]:
    """Export the public routes to a clean static directory."""
    output = output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    normalised_base = _normalise_base_path(base_path)
    written: list[Path] = []

    for route, (title, description, renderer) in _pages().items():
        destination = output / ("index.html" if route == "/" else route.strip("/"))
        destination = destination if destination.suffix else destination / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        page = _layout(title, description, route, renderer())
        destination.write_text(
            _apply_base_path(page, normalised_base), encoding="utf-8"
        )
        written.append(destination)

    (output / "static").mkdir()
    (output / "static" / "site.css").write_text(CSS, encoding="utf-8")
    (output / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    written.extend([output / "static" / "site.css", output / "robots.txt"])
    return written


def serve(host: str = HOST, port: int = PORT) -> None:
    """Run the local website server until interrupted."""

    class QuietRequestHandler(WSGIRequestHandler):
        """Keep the local development server output concise."""

        def log_message(self, format: str, *args: object) -> None:
            print(format % args)

    with make_server(
        host,
        port,
        application,
        server_class=WSGIServer,
        handler_class=QuietRequestHandler,
    ) as httpd:
        print(f"SoulMap website running at http://{host}:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSoulMap website stopped.")


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulmap web", description="Run or export the SoulMap public website."
    )
    parser.add_argument("--host", default=HOST, help=f"Bind host (default: {HOST})")
    parser.add_argument(
        "--port", type=int, default=PORT, help=f"Bind port (default: {PORT})"
    )
    parser.add_argument(
        "--export-static",
        action="store_true",
        help="Write static files instead of serving.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("site"), help="Static output directory."
    )
    parser.add_argument(
        "--base-path",
        default="",
        help="URL path prefix for a GitHub Pages project site.",
    )
    parsed = parser.parse_args(args)
    if parsed.export_static:
        written = export_static(parsed.output, parsed.base_path)
        print(f"Exported {len(written)} static website files to {parsed.output}")
        return 0
    serve(parsed.host, parsed.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
