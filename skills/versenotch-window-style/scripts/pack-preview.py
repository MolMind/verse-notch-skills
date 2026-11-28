"""Build a declarative package for the VerseNotch staging marketplace."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from zipfile import ZIP_STORED, ZipFile, ZipInfo


LAYER_OPERATIONS = {
    "material": ("solid", "frost", "graphite", "ocean", "pine", "bronze", "paper", "transparent", "black"),
    "prelude-style": ("dots", "pulse", "seven-dots", "lifeline"),
    "resonance-style": ("bars", "glow", "diaphragm", "contour", "grain", "bloom"),
}

EXAMPLES = {
    **{kind: {"operation": ops[0], "color": "#395575"} for kind, ops in LAYER_OPERATIONS.items()},
    "music-provider": {"provider": "netease"},
    "metadata-provider": {"resource": "lyrics", "source": "lrclib"},
    "window-style": {"width": 640, "height": "extended", "material": "graphite", "resonance": "off"},
    "playback-order": {"strategy": "artist-rotation", "avoidRecent": 5},
    "audio-preset": {"preampDb": -3, "bassDb": 2, "midDb": 0, "trebleDb": 1},
}


MUSIC_PROVIDER_HOSTS = {
    "kugou": {
        "playback": "gateway.kugou.com",
        "registerDevice": "userservice.kugou.com",
        "recommendations": "m.kugou.com",
        "cloudTracks": "gateway.kugou.com",
        "publicTracks": "gateway.kugou.com",
        "legacyPublicTracks": "mobiles.kugou.com",
        "qrCreate": "login-user.kugou.com",
        "qrPoll": "login-user.kugou.com",
        "ownedPlaylists": "gateway.kugou.com",
        "resolve": "m.kugou.com",
        "search": "songsearch.kugou.com",
        "lyrics": "m.kugou.com"
    },
    "netease": {
        "legacySearch": "music.163.com",
        "lyrics": "interface3.music.163.com",
        "/api/cloudsearch/pc": "interface.music.163.com",
        "/api/login/qrcode/client/login": "interface.music.163.com",
        "/api/login/qrcode/unikey": "interface.music.163.com",
        "/api/personalized/playlist": "interface.music.163.com",
        "/api/playmode/intelligence/list": "interface.music.163.com",
        "/api/radio/like": "interface.music.163.com",
        "/api/song/enhance/player/url/v1": "interface.music.163.com",
        "/api/song/like/get": "interface.music.163.com",
        "/api/user/playlist": "interface.music.163.com",
        "/api/v1/discovery/simiSong": "interface.music.163.com",
        "/api/v1/radio/get": "interface.music.163.com",
        "/api/v3/discovery/recommend/songs": "interface.music.163.com",
        "/api/v3/song/detail": "interface.music.163.com",
        "/api/v6/playlist/detail": "interface.music.163.com",
        "/api/w/nuser/account/get": "interface.music.163.com"
    },
    "qq": {
        "recommendations": "c.y.qq.com",
        "publicTracks": "c.y.qq.com",
        "qrCreate": "ssl.ptlogin2.qq.com",
        "qrPoll": "ssl.ptlogin2.qq.com",
        "checkSignature": "ssl.ptlogin2.graph.qq.com",
        "loginJump": "graph.qq.com",
        "authorize": "graph.qq.com",
        "loginCallback": "y.qq.com",
        "musicRPC": "u.y.qq.com",
        "lyrics": "c.y.qq.com",
        "legacySearch": "c.y.qq.com"
    }
}

def music_provider_valid(config):
    provider = config.get("provider")
    if not isinstance(provider, str) or provider not in MUSIC_PROVIDER_HOSTS:
        return False
    if not set(config) <= {"provider", "endpoints", "rpc"}:
        return False
    if "rpc" in config:
        rpc = config["rpc"]
        if provider != "qq" or not isinstance(rpc, dict) or not rpc:
            return False
        for operation, name in rpc.items():
            if (operation not in {"login", "ownedPlaylists", "playlistTracks", "resolve", "search"}
                    or not isinstance(name, str) or len(name) > 128
                    or not re.fullmatch(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+/[A-Za-z0-9_]+", name)):
                return False
    endpoints = config.get("endpoints", {})
    if "endpoints" in config and (not isinstance(endpoints, dict) or not endpoints):
        return False
    for operation, address in endpoints.items():
        host = MUSIC_PROVIDER_HOSTS[provider].get(operation)
        if not host or not isinstance(address, str):
            return False
        parts = urlsplit(address)
        if (address != f"https://{host}{parts.path}"
                or not re.fullmatch(r"/[a-zA-Z0-9._/&=-]{1,255}", parts.path)
                or any(part in ("", ".", "..") for part in parts.path[1:].split("/"))
                or (operation.startswith("/api/") and not parts.path.startswith("/eapi/"))):
            return False
    return True


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
    if args.type in LAYER_OPERATIONS:
        if set(config) != {"operation", "color"} or config["operation"] not in LAYER_OPERATIONS[args.type]:
            parser.error("layer config requires a supported operation and color")
        if not isinstance(config["color"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", config["color"]):
            parser.error("layer color must be #RRGGBB")
    if args.type == "music-provider":
        try:
            if not music_provider_valid(config):
                parser.error("music-provider requires a supported provider and optional trusted API endpoints")
        except ValueError as error:
            parser.error(str(error))
    requires_030 = args.type in LAYER_OPERATIONS or (args.type == "music-provider" and {"endpoints", "rpc"}.intersection(config))
    manifest = {
        "manifestVersion": 1, "id": args.id, "name": args.name, "type": args.type,
        "version": args.version, "author": args.author, "license": args.license,
        "minAppVersion": "0.3.0" if requires_030 else "0.2.0", "pluginAPIVersion": 1,
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
