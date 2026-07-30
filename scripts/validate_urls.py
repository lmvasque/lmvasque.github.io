#!/usr/bin/env python3
"""Check every resource link in _publications and _talks.

Catches the two mistakes that are easy to make by hand:

  1. A link that no longer resolves, or a local file that was renamed or moved.
  2. A resource filed under the wrong field, e.g. an ACL Anthology .mp4 talk
     recording listed as `slidesurl`, which makes the site offer "Slides" that
     turn out to be a video.

Usage:

    python3 scripts/validate_urls.py              # check everything
    python3 scripts/validate_urls.py --local-only # skip network, just check files/

Exits non-zero if anything is wrong, so it can gate a commit or a build.
Standard library only; remote checks shell out to curl.
"""

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

COLLECTIONS = ("_publications", "_talks")

# Every front-matter field that holds a URL or a path.
FIELDS = ("paperurl", "slidesurl", "posterurl", "videourl", "codeurl", "talkurl")

# Substrings expected in the content type or the URL itself. Fields absent from
# this map (paperurl, codeurl, talkurl) can legitimately point anywhere.
EXPECTED = {
    "slidesurl": ("pdf", "presentation"),
    "posterurl": ("pdf",),
    "videourl": ("mp4", "video", "youtu"),
}

VALUE = re.compile(r"""^(?P<field>[a-z]+):\s*['"]?(?P<value>[^'"\n]+?)['"]?\s*$""")


def front_matter(path):
    """Yield (field, value) for the resource fields in a file's front matter."""
    text = path.read_text(encoding="utf-8")
    head = text.split("\n---\n", 1)[0]
    for line in head.splitlines():
        match = VALUE.match(line)
        if match and match.group("field") in FIELDS:
            yield match.group("field"), match.group("value")


def check_remote(url):
    """Return (ok, detail) for a URL, following redirects."""
    result = subprocess.run(
        ["curl", "-sIL", "--max-time", "25", "-o", "/dev/null",
         "-w", "%{http_code} %{content_type}", url],
        capture_output=True, text=True,
    )
    parts = result.stdout.strip().split(" ", 1)
    status = parts[0] if parts else "000"
    ctype = parts[1] if len(parts) > 1 else ""
    return status.startswith("2"), f"HTTP {status}", ctype


def type_mismatch(field, url, ctype):
    """True if the resource does not look like what the field promises."""
    if field not in EXPECTED:
        return False
    haystack = f"{ctype} {url}".lower()
    return not any(hint in haystack for hint in EXPECTED[field])


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local-only", action="store_true",
                        help="only check paths under the repo, skip network requests")
    args = parser.parse_args()

    problems = []
    checked = 0

    for collection in COLLECTIONS:
        for path in sorted((ROOT / collection).glob("*.md")):
            for field, value in front_matter(path):
                checked += 1
                label = f"{path.name:42s} {field:10s}"

                if value.startswith("/"):
                    if (ROOT / value.lstrip("/")).is_file():
                        print(f"ok        {label} {value}")
                    else:
                        print(f"MISSING   {label} {value}")
                        problems.append(f"{path.name}: {field} -> file not found: {value}")
                    continue

                if args.local_only:
                    print(f"skipped   {label} {value}")
                    continue

                ok, detail, ctype = check_remote(value)
                note = ""
                if type_mismatch(field, value, ctype):
                    note = f"   <-- not a {field[:-3]}: {ctype or 'unknown type'}"
                    problems.append(f"{path.name}: {field} -> {ctype or 'unknown'}: {value}")

                print(f"{'ok       ' if ok else detail.ljust(9)} {label} {value[:60]}{note}")
                if not ok:
                    problems.append(f"{path.name}: {field} -> {detail}: {value}")

    print("\n" + "=" * 72)
    print(f"{checked} resource(s) found.")
    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print("  -", problem)
        return 1
    if args.local_only:
        print("All local files exist. Remote links were not checked.")
    else:
        print("All resources resolve and match their field type.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
