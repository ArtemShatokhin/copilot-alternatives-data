#!/usr/bin/env python3
"""Validate data/copilot-alternatives.yaml against schema.json and its own rules.

    python scripts/validate.py data/copilot-alternatives.yaml

Two kinds of check:
  1. shape  - required keys, types, date format, https source, no unknown keys
  2. rules  - the ones a schema cannot express and a reviewer would otherwise
              have to remember:
                * every price is a string reading as published, or "not published"
                * a row that is not open source never claims self-hosting
                * no popularity field (stars, forks, downloads) exists at all
                * a `checked` date is not in the future

Exit code 0 clean, 1 on any violation, printed one per line.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED_FIELDS = {"stars", "forks", "downloads", "github_stars", "popularity"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def mini_yaml(text: str) -> dict:
    """Parse the subset of YAML this file uses: top scalars plus a list of flat
    maps. Deliberately small so the checker needs no third-party dependency."""
    doc: dict = {"rows": []}
    current: dict | None = None
    in_rows = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^rows:\s*$", line):
            in_rows = True
            continue
        if in_rows and re.match(r"^\s{2}-\s", line):
            current = {}
            doc["rows"].append(current)
            body = re.sub(r"^\s{2}-\s", "", line)
            if body:
                k, _, v = body.partition(":")
                current[k.strip()] = v.strip()
            continue
        if in_rows and current is not None and re.match(r"^\s{4}\S", line):
            k, _, v = line.strip().partition(":")
            key, val = k.strip(), v.strip()
            if val.startswith("["):
                current[key] = [p.strip().strip('"') for p in val.strip("[]").split(",") if p.strip()]
            else:
                current[key] = val.strip('"')
            continue
        if not line.startswith(" "):
            key, _, val = line.partition(":")
            doc[key.strip()] = val.strip().strip('"')
    return doc


def check(doc: dict, schema: dict) -> list[str]:
    errs: list[str] = []
    item_req = schema["properties"]["rows"]["items"]["required"]
    allowed = set(schema["properties"]["rows"]["items"]["properties"])
    today = date.today()
    for i, row in enumerate(doc.get("rows", [])):
        where = f"row {i} ({row.get('product', '?')})"
        for key in item_req:
            if key not in row:
                errs.append(f"{where}: missing {key}")
        for key in row:
            if key in BANNED_FIELDS:
                errs.append(f"{where}: popularity field {key} is not a buying criterion")
            elif key not in allowed:
                errs.append(f"{where}: unknown field {key}")
        for key in ("open_source", "self_hosted"):
            if key in row and row[key] not in ("true", "false", True, False):
                errs.append(f"{where}: {key} must be true or false")
        src = str(row.get("source", ""))
        if src and not src.startswith("https://"):
            errs.append(f"{where}: source must be an https URL")
        for key in ("checked",):
            val = str(row.get(key, ""))
            if val and not DATE.match(val):
                errs.append(f"{where}: {key} must be YYYY-MM-DD")
            elif val and datetime.strptime(val, "%Y-%m-%d").date() > today:
                errs.append(f"{where}: {key} is in the future")
        if str(row.get("open_source")) == "false" and str(row.get("self_hosted")) == "true":
            errs.append(f"{where}: not open source but claims self-hosting")
        if "price" in row and not str(row["price"]).strip():
            errs.append(f"{where}: price must say a figure or 'not published'")
    if not doc.get("rows"):
        errs.append("no rows")
    return errs


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/copilot-alternatives.yaml"
    schema = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))
    doc = mini_yaml(path.read_text(encoding="utf-8"))
    errs = check(doc, schema)
    for e in errs:
        print(e)
    print(f"{len(doc.get('rows', []))} rows, {len(errs)} problem(s)")
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
