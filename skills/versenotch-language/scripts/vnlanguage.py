#!/usr/bin/env python3
"""Validate and package a VerseNotch language plugin."""

import argparse
import io
import json
from pathlib import Path
import re
import sys
import zipfile


LIMIT = 256 * 1024
VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}")
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*){2,}")
LOCALE = re.compile(r"[a-z]{2,3}(?:-[A-Z][a-z]{3})?(?:-(?:[A-Z]{2}|[0-9]{3}))?")
PLACEHOLDER = re.compile(r"\{[0-9]+\}")
FILES = {"manifest.json": 64 * 1024, "strings.json": LIMIT}
SETTINGS = {
    "manifestVersion": 1,
    "pluginAPIVersion": 1,
    "type": "language",
    "entry": "strings.json",
    "permissions": [],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_limited(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, f"{path.name} exceeds {limit} bytes")
    return data


def read_files(source):
    if source.is_dir():
        require({p.name for p in source.iterdir()} == FILES.keys(), "Use only manifest.json and strings.json")
        return {name: read_limited(source / name, limit) for name, limit in FILES.items()}
    require(source.suffix == ".vnplugin", "Use the .vnplugin extension")
    with zipfile.ZipFile(io.BytesIO(read_limited(source, LIMIT))) as archive:
        entries = archive.infolist()
        require(not archive.comment and len(entries) == 2 and
                {entry.filename for entry in entries} == FILES.keys(),
                "The ZIP root must contain only manifest.json and strings.json")
        for entry in entries:
            require(entry.file_size <= FILES[entry.filename] and entry.flag_bits & ~0x800 == 0
                    and entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    and (entry.external_attr >> 16) & 0xF000 in (0, 0x8000),
                    f"Invalid ZIP entry: {entry.filename}")
        return {name: archive.read(name) for name in FILES}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def version(value):
    require(isinstance(value, str) and len(value) <= 32 and VERSION.fullmatch(value), "Use a three-part version")
    parts = tuple(map(int, value.split(".")))
    require(all(part <= 2**63 - 1 for part in parts), "Version component out of range")
    return parts


def validate(files, catalog):
    manifest = json.loads(files["manifest.json"].decode("utf-8"), object_pairs_hook=unique_object)
    fields = {"id", "name", "author", "license", "version", "minAppVersion", *SETTINGS}
    require(isinstance(manifest, dict) and manifest.keys() == fields, "Invalid manifest fields")
    for key, expected in SETTINGS.items():
        require(type(manifest[key]) is type(expected) and manifest[key] == expected, f"Invalid {key}")
    identifier = manifest["id"]
    require(isinstance(identifier, str) and len(identifier) <= 128 and IDENTIFIER.fullmatch(identifier)
            and not identifier.startswith(("builtin.", "com.verse-notch.")), "Invalid plugin ID")
    for key, limit in (("name", 80), ("author", 100), ("license", 100)):
        text = manifest[key]
        require(isinstance(text, str) and text and text == text.strip() and len(text.encode("utf-8")) <= limit,
                f"Invalid {key}")
    version(manifest["version"])
    require(version(manifest["minAppVersion"]) >= (0, 2, 5), "minAppVersion must be at least 0.2.5")

    strings = json.loads(files["strings.json"].decode("utf-8"), object_pairs_hook=unique_object)
    require(isinstance(strings, dict) and strings.keys() == {"locale", "translations"}, "Invalid strings.json fields")
    locale = strings["locale"]
    require(isinstance(locale, str) and LOCALE.fullmatch(locale), "Invalid locale")
    entries = strings["translations"]
    require(isinstance(entries, list) and entries, "Add at least one translation")
    seen = set()
    for entry in entries:
        require(isinstance(entry, list) and len(entry) == 2 and all(isinstance(item, str) for item in entry),
                "Each translation must contain a key and a string")
        key, value = entry
        require(key in catalog and key not in seen, f"Unknown or duplicate key: {key}")
        require(value.strip() and len(value.encode("utf-8")) <= 2048 and
                all(ord(char) >= 32 or char in "\t\n" for char in value), f"Invalid text: {key}")
        require(sorted(PLACEHOLDER.findall(value)) == sorted(PLACEHOLDER.findall(catalog[key])),
                f"Placeholder mismatch: {key}")
        seen.add(key)
    return locale, len(seen)


def pack(files, destination):
    require(destination.suffix == ".vnplugin", "Use the .vnplugin extension")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    require(buffer.tell() <= LIMIT, "Package exceeds 256 KiB")
    with destination.open("xb") as stream:
        stream.write(buffer.getbuffer())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.add_subparsers(dest="command", required=True)
    args.add_parser("validate").add_argument("source", type=Path)
    packaging = args.add_parser("pack")
    packaging.add_argument("source", type=Path)
    packaging.add_argument("destination", type=Path)
    options = parser.parse_args()
    try:
        if options.command == "pack":
            require(options.source.is_dir(), "Pack a source directory")
        files = read_files(options.source)
        manifest = json.loads(files["manifest.json"].decode("utf-8"), object_pairs_hook=unique_object)
        require(isinstance(manifest, dict), "Invalid manifest")
        revision = "0.3.0" if version(manifest.get("minAppVersion", "")) >= (0, 3, 0) else "0.2.5"
        catalog_path = Path(__file__).resolve().parents[1] / "references" / f"strings-{revision}.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        locale, translated = validate(files, catalog)
        if options.command == "pack":
            pack(files, options.destination)
        print(f"{locale}: {translated}/{len(catalog)} translated ({translated / len(catalog):.1%})")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
