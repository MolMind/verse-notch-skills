"""Build a declarative package for the VerseNotch staging marketplace."""
import argparse
import json
from pathlib import Path
import re
from zipfile import ZIP_STORED, ZipFile, ZipInfo


EXAMPLES = {
    "music-provider": {"provider": "netease"},
    "metadata-provider": {"resource": "lyrics", "source": "lrclib"},
    "window-style": {"width": 640, "height": "extended", "material": "graphite", "resonance": "off"},
    "playback-order": {"strategy": "artist-rotation", "avoidRecent": 5},
    "audio-preset": {"preampDb": -3, "bassDb": 2, "midDb": 0, "trebleDb": 1},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("type", choices=EXAMPLES)
    parser.add_argument("output", type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--config", type=Path, help="custom config.json; defaults to the reference example")
    args = parser.parse_args()
    identity = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*){2,}"
    version = r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}"
    if not re.fullmatch(identity, args.id) or len(args.id) > 128 or args.id.startswith(("builtin.", "com.verse-notch.")):
        parser.error("--id must be a non-reserved reverse-domain identifier")
    if not re.fullmatch(version, args.version) or len(args.version) > 32:
        parser.error("--version must have three numeric components")
    for field, value, limit in (("name", args.name, 80), ("author", args.author, 100), ("license", args.license, 100)):
        if not value.strip() or value != value.strip() or len(value.encode()) > limit:
            parser.error(f"--{field} is empty, untrimmed, or over {limit} bytes")
    if args.output.suffix != ".vnplugin":
        parser.error("output must end with .vnplugin")
    config = EXAMPLES[args.type]
    if args.config:
        try:
            with args.config.open("rb") as source:
                raw = source.read(64 * 1024 + 1)
            if len(raw) > 64 * 1024:
                parser.error("config must not exceed 64 KiB")
            config = json.loads(raw)
            if not isinstance(config, dict):
                parser.error("config must be a JSON object")
        except (OSError, ValueError) as error:
            parser.error(str(error))
    manifest = {
        "manifestVersion": 1, "id": args.id, "name": args.name, "type": args.type,
        "version": args.version, "author": args.author, "license": args.license,
        "minAppVersion": "0.2.0", "pluginAPIVersion": 1,
        "entry": "config.json", "permissions": [],
    }
    try:
        entries = {
            name: json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            for name, value in (("manifest.json", manifest), ("config.json", config))
        }
        if any(len(value) > 64 * 1024 for value in entries.values()):
            parser.error("encoded manifest and config must each fit within 64 KiB")
        with ZipFile(args.output, "x", ZIP_STORED) as archive:
            for name, body in entries.items():
                archive.writestr(ZipInfo(name), body)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"{args.output} · {args.type} · pending marketplace validation")


if __name__ == "__main__":
    main()
