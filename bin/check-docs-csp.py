#!/usr/bin/env python3
"""
Check that a built docs site serves its own scripts, style sheets, and fonts.

Fails when:

- there are no pages, or a page is missing the Content-Security-Policy
- a page's policy isn't in <head> ahead of every script, style sheet, and
  iframe, since browsers ignore it there or apply it only to what follows
- the policy has no default-src, lets anything but images, media, and
  connections load from another host, or allows a frame source other than
  the site and the --frame-src sources
- a page's <script> or style sheet <link> points at another host, or its
  <iframe> at a URL the policy blocks
- a .js or .css file in the site contains a script, style sheet, or font URL
  on another host, since the theme loads libraries like mermaid at runtime.
  CDN URLs for a package in docs-vendor are fine if the major versions
  match. Pass --unused for URLs of features the site doesn't use.
- a page has a mermaid diagram but doesn't load javascripts/mermaid.js, since
  the theme would then fall back to a CDN copy the policy blocks
"""

from argparse import ArgumentParser, ArgumentTypeError
from collections.abc import Iterator
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import sys

URL_RE = re.compile(r"https?://[\w.-]+(?::\d+)?/[\w.@/%+~-]*")
CDN_PACKAGE_RE = re.compile(r"https://(?:unpkg\.com|cdn\.jsdelivr\.net/npm)/((?:@[\w.-]+/)?[\w.-]+)@(\d+)/")
CDN_HOSTS = {
    "unpkg.com",
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
    "fonts.googleapis.com",
}
FETCHED_SUFFIXES = (".js", ".mjs", ".css", ".woff2", ".woff", ".ttf", ".otf")
OPEN_DIRECTIVES = {"img-src", "media-src", "connect-src", "frame-src"}
SELF_ONLY_SOURCES = {"'self'", "'unsafe-inline'", "'none'"}
MERMAID_LOADER = "javascripts/mermaid.js"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.policy: str | None = None
        self.in_head = False
        self.problems: list[str] = []
        self.resources: list[tuple[str, str]] = []
        self.has_mermaid = False
        self.loads_mermaid = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if "mermaid" in (a.get("class") or "").split():
            self.has_mermaid = True
        if tag in ("head", "body"):
            self.in_head = tag == "head"
        if tag == "meta" and a.get("http-equiv") == "Content-Security-Policy":
            if not self.in_head:
                self.problems.append("policy <meta> tag is outside <head>")
            self.policy = a.get("content")
            return
        is_stylesheet = tag == "link" and a.get("rel") == "stylesheet"
        if self.policy is None and (tag in ("script", "iframe") or is_stylesheet):
            self.problems.append(f"<{tag}> comes before the policy <meta> tag")
        if tag == "script" and (src := a.get("src")):
            self.resources.append(("script-src", src))
            self.loads_mermaid |= src.endswith(MERMAID_LOADER)
        elif is_stylesheet and (href := a.get("href")):
            self.resources.append(("style-src", href))
        elif tag == "iframe" and (src := a.get("src")):
            self.resources.append(("frame-src", src))

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False


def parse_policy(policy: str) -> dict[str, list[str]]:
    directives: dict[str, list[str]] = {}
    for part in policy.split(";"):
        if part.strip():
            name, *sources = part.split()
            directives.setdefault(name.lower(), sources)
    return directives


def source_allows(source: str, url: str) -> bool:
    target = urlsplit(url)
    allowed = urlsplit(source)
    if allowed.scheme != target.scheme or allowed.netloc != target.netloc:
        return False
    if allowed.path in ("", "/"):
        return True
    if allowed.path.endswith("/"):
        return target.path.startswith(allowed.path)
    return target.path == allowed.path


def policy_problems(directives: dict[str, list[str]], frame_sources: set[str]) -> Iterator[str]:
    if "default-src" not in directives:
        yield "policy has no default-src"
    for directive, sources in directives.items():
        if not directive.endswith(("-src", "-src-elem", "-src-attr")):
            continue
        if directive in OPEN_DIRECTIVES:
            continue
        allowed = SELF_ONLY_SOURCES | ({"data:"} if directive == "font-src" else set())
        for source in sources:
            if source not in allowed:
                yield f"policy allows {source} in {directive}"
    for source in directives.get("frame-src", []):
        if source != "'self'" and source not in frame_sources:
            yield f"policy allows {source} in frame-src; pass it with --frame-src"


GITLAB_FRAME_HOSTS = {"gitlab.com", "projects.gitlab.io", "thelabnyc.gitlab.io"}


def gitlab_frame_source(value: str) -> str:
    if not value.startswith("https://") or urlsplit(value).hostname not in GITLAB_FRAME_HOSTS:
        raise ArgumentTypeError("frames may only come from our own GitLab")
    return value


def vendored_versions(manifest: Path) -> dict[str, str]:
    assets = json.loads((manifest / "package.json").read_text()).get("docsAssets", {})
    packages = json.loads((manifest / "package-lock.json").read_text())["packages"]
    return {str(name): str(packages[f"node_modules/{name}"]["version"]) for name in assets}


def runtime_problems(site: Path, vendored: dict[str, str], unused: tuple[str, ...]) -> Iterator[str]:
    files = sorted([*site.rglob("*.js"), *site.rglob("*.mjs"), *site.rglob("*.css")])
    for file in files:
        for url in sorted(set(URL_RE.findall(file.read_text(errors="replace")))):
            parts = urlsplit(url)
            fetched = parts.path.endswith(FETCHED_SUFFIXES) or parts.netloc in CDN_HOSTS
            if not fetched or url.startswith(unused):
                continue
            if package := CDN_PACKAGE_RE.match(url):
                name, major = package.groups()
                if name in vendored:
                    if vendored[name].split(".")[0] != major:
                        yield f"{file}: loads {name}@{major}, but docs-vendor has {name} {vendored[name]}"
                    continue
            yield f"{file}: loads {url} from another host"


def check(
    site: Path,
    vendored: dict[str, str],
    unused: tuple[str, ...],
    frame_sources: set[str],
) -> Iterator[str]:
    pages = sorted(site.rglob("*.html"))
    if not pages:
        yield f"{site}: no HTML pages found"
        return
    policies: dict[str, dict[str, list[str]]] = {}
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text())
        for problem in parser.problems:
            yield f"{page}: {problem}"
        if parser.has_mermaid and not parser.loads_mermaid:
            yield f"{page}: has a mermaid diagram but doesn't load {MERMAID_LOADER}"
        if parser.policy is None:
            yield f"{page}: no Content-Security-Policy meta tag"
            continue
        directives = policies.setdefault(parser.policy, parse_policy(parser.policy))
        for directive, url in parser.resources:
            if url.startswith("//"):
                url = f"https:{url}"
            if not urlsplit(url).scheme:
                continue
            if directive != "frame-src":
                yield f"{page}: {directive} {url} is on another host"
                continue
            sources = directives.get("frame-src", directives.get("default-src", []))
            if not any(source_allows(s, url) for s in sources):
                yield f"{page}: frame-src blocks {url}"
    for directives in policies.values():
        yield from policy_problems(directives, frame_sources)
    yield from runtime_problems(site, vendored, unused)


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--vendor-manifest", type=Path, default=Path("docs-vendor"))
    parser.add_argument(
        "--unused",
        action="append",
        default=[],
        metavar="URL_PREFIX",
        help="runtime URL the site never loads",
    )
    parser.add_argument(
        "--frame-src",
        action="append",
        default=[],
        type=gitlab_frame_source,
        metavar="SOURCE",
        help="GitLab source the policy may allow in frame-src",
    )
    args = parser.parse_args()
    site: Path = args.site
    manifest: Path = args.vendor_manifest
    unused: list[str] = args.unused
    frame_sources: list[str] = args.frame_src
    vendored = vendored_versions(manifest)
    problems = list(check(site, vendored, tuple(unused), set(frame_sources)))
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
