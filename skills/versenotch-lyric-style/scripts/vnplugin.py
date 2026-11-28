"""Validate and pack VerseNotch lyric-style v1 through v4 without extracting ZIP input."""

import argparse
import json
from pathlib import Path
import re
import stat
import sys
import zipfile


MAX_ARCHIVE = 10 * 1024**2
MAX_TOTAL = 30 * 1024**2
MAX_FILES = 100
RULES = Path(__file__).resolve().parents[1] / "references"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    require(len(name) <= 180 and all(re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", part)
                                     for part in name.split("/")), f"Invalid path: {name!r}")


def check_entries(entries):
    require(len(entries) <= MAX_FILES, "Too many files (maximum 100)")
    require(sum(length for _, length in entries) <= MAX_TOTAL, "Contents exceed 30 MiB")
    names = set()
    for name, _ in entries:
        safe_name(name)
        require(name.lower() not in names, f"Duplicate path: {name}")
        names.add(name.lower())


def read_files(path):
    require(not path.is_symlink(), "Symbolic links are not allowed")
    if path.is_dir():
        files = []
        for item in path.rglob("*"):
            mode = item.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            require(stat.S_ISREG(mode), f"Not a regular file: {item}")
            files.append((item.relative_to(path).as_posix(), item))
            require(len(files) <= MAX_FILES, "Too many files (maximum 100)")
        check_entries([(name, item.stat().st_size) for name, item in files])
        return {name: item.read_bytes() for name, item in files}
    require(path.suffix == ".vnplugin", "Use a source directory or a .vnplugin file")
    require(path.stat().st_size <= MAX_ARCHIVE, "Archive exceeds 10 MiB")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        for item in entries:
            mode = stat.S_IFMT(item.external_attr >> 16)
            require(not item.is_dir() and mode in (0, stat.S_IFREG), f"Not a regular file: {item.filename}")
            require(item.orig_filename == item.filename and not (item.flag_bits & 1), "Invalid ZIP filename or encrypted entry")
            require(item.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), "Unsupported ZIP compression")
        check_entries([(item.filename, item.file_size) for item in entries])
        return {item.filename: archive.read(item) for item in entries}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_schema(value, rule, root, label):
    if "$ref" in rule:
        validate_schema(value, root["$defs"][rule["$ref"].split("/")[-1]], root, label)
        return
    if "oneOf" in rule:
        if isinstance(value, dict):
            for option in rule["oneOf"]:
                if "type" in value and value["type"] == option.get("properties", {}).get("type", {}).get("const"):
                    validate_schema(value, option, root, label)
                    return
        matches = 0
        for option in rule["oneOf"]:
            try:
                validate_schema(value, option, root, label)
                matches += 1
            except ValueError:
                continue
        require(matches == 1, f"{label}: expected a supported configuration and its required fields")
        return
    kind = rule.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int}
    require(kind is None or type(value) is types[kind], f"{label}: expected {kind}")
    if "const" in rule:
        require(type(value) is type(rule["const"]) and value == rule["const"], f"{label}: invalid value")
    if "enum" in rule:
        require(value in rule["enum"], f"{label}: expected one of {rule['enum']}")
    if kind == "object":
        properties = rule["properties"]
        forbidden = rule.get("not", {}).get("required", [])
        require(not forbidden or not all(key in value for key in forbidden),
                f"{label}: mutually exclusive fields: {', '.join(forbidden)}")
        require(not (set(rule["required"]) - value.keys()), f"{label}: missing required fields")
        require(not (value.keys() - properties.keys()), f"{label}: unknown fields")
        for key, entry in value.items():
            validate_schema(entry, properties[key], root, f"{label}.{key}")
    if kind == "string":
        require(rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", 1_000_000), f"{label}: invalid length")
        if "pattern" in rule:
            matched = re.search(rule["pattern"], value)
            require(matched is not None and (not rule["pattern"].endswith("$") or matched.end() == len(value)),
                    f"{label}: invalid format")
    if kind == "integer":
        require(rule.get("minimum", -sys.maxsize) <= value <= rule.get("maximum", sys.maxsize), f"{label}: out of range")
    if kind == "array":
        require(rule.get("minItems", 0) <= len(value) <= rule.get("maxItems", MAX_FILES), f"{label}: invalid item count")
        if "items" in rule:
            for entry in value:
                validate_schema(entry, rule["items"], root, f"{label}[]")


def image_size(data, suffix):
    if suffix == ".png":
        require(data.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR") and len(data) >= 33, "Invalid PNG header")
        offset = 8
        kind = None
        while offset + 12 <= len(data):
            length = int.from_bytes(data[offset:offset + 4], "big")
            kind = data[offset + 4:offset + 8]
            require(kind != b"acTL", "Use a single PNG image or a v2 sprite sheet")
            offset += length + 12
            require(offset <= len(data), "Truncated PNG chunk")
            if kind == b"IEND":
                break
        require(kind == b"IEND", "Missing PNG end chunk")
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    require(data.startswith(b"\xff\xd8"), "Invalid JPEG header")
    offset = 2
    while offset < len(data) and data[offset] == 255:
        while offset < len(data) and data[offset] == 255:
            offset += 1
        if offset + 2 >= len(data):
            break
        marker = data[offset]
        length = int.from_bytes(data[offset + 1:offset + 3], "big")
        if length < 2 or offset + 1 + length > len(data) or marker in (0xD9, 0xDA):
            break
        if marker in (0xC0, 0xC1, 0xC2) and length >= 8:
            return int.from_bytes(data[offset + 6:offset + 8], "big"), int.from_bytes(data[offset + 4:offset + 6], "big")
        offset += 1 + length
    raise ValueError("Unrecognized JPEG size (expected baseline or progressive JPEG)")


def json_entry(files, name):
    require(name in files, f"Missing root file: {name}")
    require(len(files[name]) <= 64 * 1024, f"{name}: exceeds 64 KiB")
    return json.loads(files[name].decode("utf-8"), object_pairs_hook=unique_pairs)


def version_tuple(value):
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value),
            "Expected an app version such as 0.2.2")
    return tuple(map(int, value.split(".")))


def validate(files, host_version=None):
    manifest = json_entry(files, "manifest.json")
    require(isinstance(manifest, dict), "manifest.json: expected object")
    api = manifest.get("pluginAPIVersion")
    require(type(api) is int and api in (1, 2, 3, 4), "Expected lyric-style plugin API 1 through 4")
    style = json_entry(files, "style.json")
    for name, value in (("manifest", manifest), ("style", style)):
        schema_version = 3 if name == "style" and api == 4 else api
        schema = json.loads((RULES / f"{name}-v{schema_version}.schema.json").read_text(encoding="utf-8"))
        validate_schema(value, schema, schema, f"{name}.json")
    for key, limit in (("name", 80), ("author", 100), ("license", 100)):
        text = manifest[key]
        require(text == text.strip() and len(text.encode("utf-8")) <= limit,
                f"manifest.json: {key} must be trimmed and fit within {limit} UTF-8 bytes")
    minimum = version_tuple(manifest["minAppVersion"])
    floor = (0, 3, 0) if api == 4 else (0, 2, api)
    require(api == 1 or minimum >= floor, f"minAppVersion below API {api} floor")
    if host_version is not None:
        require(version_tuple(host_version) >= minimum,
                f"Target VerseNotch {host_version} is older than required {manifest['minAppVersion']}")
    expected = {"manifest.json", "style.json"}
    if api == 4:
        if "assets/cover.png" in files:
            cover = files["assets/cover.png"]
            width, height = image_size(cover, ".png")
            require(len(cover) <= 1024 * 1024 and 0 < width <= 1024 and 0 < height <= 1024, "Invalid catalog cover")
            expected.add("assets/cover.png")
        theme = json_entry(files, "theme.json")
        schema = json.loads((RULES / "theme-v4.schema.json").read_text(encoding="utf-8"))
        validate_schema(theme, schema, schema, "theme.json")
        require(theme["scatter"] != "glyph" or theme.get("glyphMotion") == "ripple", "glyph scatter requires ripple motion")
        if theme.get("lineLayout") == "double":
            require("stage.json" not in files and theme.get("glyphMotion") in (None, "glow", "lift", "reveal", "wipe"),
                    "double layout requires the standard text canvas and a compatible glyph motion")
        if composition := theme.get("composition"):
            require(theme.get("windowCoverage") == "full" and "stage.json" not in files and
                    "lineLayout" not in theme and "glyphMotion" not in theme,
                    "composition requires full coverage and owns the cue layout")
            required_art = {
                "portrait-chat": (("assets/portraits.png", 3, 4),),
                "conversation": (("assets/portraits.png", 3, 4),),
                "rain-footsteps": (("assets/paper.png", 1, 1), ("assets/footsteps.png", 6, 4)),
                "paper-journey": (("assets/back.jpg", 4, 6), ("assets/steps.jpg", 4, 9)),
                "fog-glass": (("assets/amber-lights.jpg", 1, 1), ("assets/condensation.jpg", 1, 1), ("assets/elevated-night.jpg", 1, 1)),
            }
            for name, columns, rows in required_art.get(composition, ()):
                require(name in files, f"Missing composition artwork: {name}")
                width, height = image_size(files[name], Path(name).suffix)
                require(columns <= width <= 4096 and rows <= height <= 4096 and width * height <= 4_000_000,
                        f"Invalid composition artwork: {name}")
                expected.add(name)
            if composition == "fog-glass":
                import base64
                import binascii
                name = "assets/finger-strokes.json"
                data = files.get(name, b"")
                require(0 < len(data) <= 6 * 1024 * 1024, "Invalid handwriting table")
                table = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs)
                require(isinstance(table, dict) and 1 <= len(table) <= 40_000, "Invalid handwriting table")
                try:
                    require(all(isinstance(value, str) and 1 <= len(base64.b64decode(value, validate=True)) <= 2048
                                for value in table.values()), "Invalid handwriting entries")
                except (ValueError, binascii.Error):
                    require(False, "Invalid handwriting entries")
                expected.add(name)
                for filename in ("notice.txt", "copying.txt", "arphicpl.txt"):
                    name = "assets/" + filename
                    require(1 <= len(files.get(name, b"")) <= 65_536, f"Missing or invalid notice: {name}")
                    expected.add(name)
        expected.add("theme.json")
        if "stage.json" in files:
            stage = json_entry(files, "stage.json")
            schema = json.loads((RULES / "stage-v4.schema.json").read_text(encoding="utf-8"))
            validate_schema(stage, schema, schema, "stage.json")
            frames = [stage["desktopFrame"], *(caption["frame"] for caption in stage["captions"])]
            for frame in frames:
                require(frame["x"] + frame["width"] <= 1000 and frame["y"] + frame["height"] <= 1000,
                        "stage.json: frame exceeds canvas")
            total_pixels = 0
            for shot in stage["gapShots"]:
                path = shot["asset"]
                require(path in files, f"Missing stage asset: {path}")
                width, height = image_size(files[path], Path(path).suffix)
                total_pixels += width * height
                require(0 < width <= 4096 and 0 < height <= 4096 and total_pixels <= 16000000 and
                        width % shot["columns"] == 0 and height % shot["rows"] == 0,
                        "stage.json: invalid sheet dimensions or pixel budget")
                expected.add(path)
            expected.add("stage.json")
    background = style["background"]
    kind = background["type"]
    require((kind == "scene") == (style["transition"]["effect"] == "scene"),
            "Scene background and scene transition must be used together")
    if kind in ("image", "scroll", "frames", "scene"):
        asset = background["asset"]
        require(asset in files, f"Missing image: {asset}")
        width, height = image_size(files[asset], Path(asset).suffix)
        require(1 <= width <= 4096 and 1 <= height <= 4096, "Image dimensions exceed 4096 × 4096")
        if kind in ("scroll", "scene"):
            require(width >= height, "Loop image must be at least as wide as it is tall")
        if kind == "scene":
            positions = [anchor["x"] for anchor in background["anchors"]]
            require(len(positions) == len(set(positions)), "Scene anchors need distinct x positions")
            foreground = background["foreground"]
            require(foreground != asset and foreground in files, f"Missing distinct foreground image: {foreground}")
            require(image_size(files[foreground], ".png") == (width, height), "Scene layers need identical dimensions")
            require(files[foreground][25] in (4, 6), "Scene foreground needs a PNG alpha channel")
            expected.add(foreground)
        if kind == "frames":
            columns, rows = background["columns"], background["rows"]
            count = columns * rows
            require(count >= 2 and width % columns == 0 and height % rows == 0,
                    "Sprite sheet needs at least 2 frames with equally sized integer cells")
            require(background["durationMs"] >= count * 34, "Sprite sheet needs at least 34 ms per frame")
        expected.add(asset)
    font_asset = style["text"].get("fontAsset")
    if font_asset:
        require(font_asset in files, f"Missing font: {font_asset}")
        font = files[font_asset]
        signature = b"OTTO" if font_asset.endswith(".otf") else bytes((0, 1, 0, 0))
        require(12 <= len(font) <= 8 * 1024 * 1024 and font.startswith(signature),
                "Expected a matching single TTF/OTF font up to 8 MiB")
        expected.add(font_asset)
    require(set(files) == expected, f"Undeclared files: {', '.join(sorted(set(files) - expected))}")
    return manifest


def pack(source, output, host_version=None):
    require(source.is_dir(), "pack requires a source directory")
    require(output.suffix == ".vnplugin", "Output must end in .vnplugin")
    require(not output.resolve().is_relative_to(source.resolve()), "Output must be outside the source directory")
    files = read_files(source)
    manifest = validate(files, host_version)
    with output.open("xb") as handle:
        try:
            with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for name, data in sorted(files.items()):
                    entry = zipfile.ZipInfo(name)
                    entry.create_system = 3
                    entry.external_attr = (stat.S_IFREG | 0o644) << 16
                    archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED)
            require(handle.tell() <= MAX_ARCHIVE, "Archive exceeds 10 MiB")
        except BaseException:
            handle.close()
            output.unlink(missing_ok=True)
            raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate_parser = subcommands.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--host-version")
    pack_parser = subcommands.add_parser("pack")
    pack_parser.add_argument("source", type=Path)
    pack_parser.add_argument("output", type=Path)
    pack_parser.add_argument("--host-version")
    args = parser.parse_args()
    try:
        manifest = validate(read_files(args.path), args.host_version) if args.command == "validate" else pack(args.source, args.output, args.host_version)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as error:
        print(f"Invalid: {error}", file=sys.stderr)
        return 1
    print(f"Valid package: {manifest['id']} {manifest['version']} (lyric-style v{manifest['pluginAPIVersion']}; not previewed in App)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
