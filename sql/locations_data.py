"""
Dynamic mapping of all Kenyan counties ➜ sub-counties ➜ wards.

Data source (MIT-licensed):
https://github.com/michaelnjuguna/Kenyan-counties-their-subcounties-and-wards-in-json-yaml-mysql-csv-latex-xlsx-Bson-markdown-and-xml
"""

from __future__ import annotations
import json
import pathlib
import urllib.request
from typing import Dict, List, TypedDict, Final

_RAW_URL: Final[str] = (
    "https://raw.githubusercontent.com/"
    "michaelnjuguna/"
    "Kenyan-counties-their-subcounties-and-wards-in-json-yaml-mysql-csv-latex-xlsx-Bson-markdown-and-xml/"
    "main/county.json"
)
_CACHE_FILE = pathlib.Path(__file__).with_suffix(".cache.json")


class _SubCountyDict(TypedDict):
    name: str
    subcounties: Dict[str, List[str]]


def _download_source() -> list[dict]:
    with urllib.request.urlopen(_RAW_URL, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _transform(raw: list[dict]) -> Dict[str, _SubCountyDict]:
    out: Dict[str, _SubCountyDict] = {}
    for county in raw:
        code = f"{county['county_code']:03d}"  # zero-pad, e.g. 1 ➜ "001"
        subs = {
            sc["constituency_name"]: sc["wards"]
            for sc in county["constituencies"]
        }
        out[code] = {"name": county["county_name"], "subcounties": subs}
    return out


def _load() -> Dict[str, _SubCountyDict]:
    # Use a tiny on-disk cache so you only hit GitHub once.
    if _CACHE_FILE.exists():
        return json.loads(_CACHE_FILE.read_text())
    data = _transform(_download_source())
    _CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data


# Your constant — access it just like before.
KENYA_LOCATIONS: Final = _load()
