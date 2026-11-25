#!/usr/bin/env python3
"""Apply an instance configuration to a RustDesk source tree.

Usage:
    apply.py --instance <instance-dir> --source <rustdesk-checkout> [--check]
    apply.py --instance <instance-dir> --validate-only

The instance directory holds `client.env`, `custom.json`, `branding/` and an
optional `patches/` directory (see `template/` for a working example).

Every edit is checked: if an expected pattern is missing from the RustDesk
sources the script stops with an error instead of silently producing a
half-branded client. This is what makes a RustDesk upgrade safe to attempt.

Only the Python standard library is required, plus Pillow for the icons.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

GENERATOR_ROOT = Path(__file__).resolve().parent.parent

# Values shipped by upstream RustDesk that the script replaces.
UPSTREAM_SERVER = "rs-ny.rustdesk.com"
UPSTREAM_KEY = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw="
UPSTREAM_API = "https://admin.rustdesk.com"
UPSTREAM_ACCENT = "0071FF"

REQUIRED_KEYS = ("APP_NAME", "COMPANY", "BUNDLE_ID", "SERVER_HOST", "SERVER_KEY")
KNOWN_KEYS = REQUIRED_KEYS + (
    "API_URL",
    "WEBSITE_URL",
    "SOURCE_URL",
    "ACCENT_COLOR",
)


class ApplyError(Exception):
    """A configuration or patching problem the user has to fix."""


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


def read_env(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE file without executing it (it is never sourced)."""
    if not path.is_file():
        raise ApplyError(f"missing configuration file: {path}")
    values: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            raise ApplyError(f"{path.name}:{number}: expected KEY=VALUE, got: {raw}")
        if key not in KNOWN_KEYS:
            raise ApplyError(f"{path.name}:{number}: unknown key {key}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def validate(config: dict[str, str]) -> None:
    missing = [key for key in REQUIRED_KEYS if not config.get(key)]
    if missing:
        raise ApplyError("client.env: missing value for " + ", ".join(missing))

    # The name ends up in file names, shell commands and Windows resources.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}", config["APP_NAME"]):
        raise ApplyError(
            "client.env: APP_NAME must be 1 to 40 characters among letters, "
            "digits, space, dot, dash and underscore"
        )
    if config["APP_NAME"].strip() != config["APP_NAME"]:
        raise ApplyError("client.env: APP_NAME must not start or end with a space")
    if config["APP_NAME"].lower() == "rustdesk":
        # RustDesk decides it is a custom client by comparing the name, and
        # the upstream name is a trademark of its owner.
        raise ApplyError("client.env: APP_NAME must differ from 'RustDesk'")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .,&_-]{0,79}", config["COMPANY"]):
        raise ApplyError("client.env: COMPANY contains unsupported characters")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*(\.[A-Za-z][A-Za-z0-9-]*){2,}", config["BUNDLE_ID"]):
        raise ApplyError("client.env: BUNDLE_ID must look like org.example.remotesupport")
    if not re.fullmatch(r"[A-Za-z0-9.-]+(:[0-9]{1,5})?", config["SERVER_HOST"]):
        raise ApplyError("client.env: SERVER_HOST must be a host name, optionally with :port")
    try:
        key_ok = len(base64.b64decode(config["SERVER_KEY"], validate=True)) == 32
    except ValueError:
        key_ok = False
    if not key_ok:
        raise ApplyError(
            "client.env: SERVER_KEY must be the server public key "
            "(content of id_ed25519.pub, 44 base64 characters)"
        )
    for key in ("API_URL", "WEBSITE_URL", "SOURCE_URL"):
        value = config.get(key, "")
        if value and not re.fullmatch(r"https?://[A-Za-z0-9._~:/?#@!&()*+,;=%-]+", value):
            raise ApplyError(f"client.env: {key} must be an http(s) URL")
    accent = config.get("ACCENT_COLOR", "")
    if accent and not re.fullmatch(r"#[0-9A-Fa-f]{6}", accent):
        raise ApplyError("client.env: ACCENT_COLOR must look like #1A2B3C")


def build_custom_client(instance: Path, config: dict[str, str]) -> dict:
    """Merge `custom.json` with the values that come from `client.env`."""
    path = instance / "custom.json"
    try:
        custom = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except json.JSONDecodeError as error:
        raise ApplyError(f"custom.json is not valid JSON: {error}") from error
    if not isinstance(custom, dict):
        raise ApplyError("custom.json must contain a JSON object")
    for section in ("default-settings", "override-settings"):
        if not isinstance(custom.setdefault(section, {}), dict):
            raise ApplyError(f"custom.json: {section} must be an object")
    for section in ("default-settings", "override-settings"):
        for name, value in custom[section].items():
            if not isinstance(value, str):
                raise ApplyError(f"custom.json: {section}.{name} must be a string")
    for name in ("password", "salt"):
        if any(name in scope for scope in (custom, custom["default-settings"], custom["override-settings"])):
            # The file is compiled into a binary anyone can download.
            raise ApplyError(
                f"custom.json: '{name}' is not allowed, a preset password "
                "would be readable by anyone holding the client"
            )

    custom["app-name"] = config["APP_NAME"]
    forced = custom["override-settings"]
    forced["custom-rendezvous-server"] = config["SERVER_HOST"]
    forced["key"] = config["SERVER_KEY"]
    if config.get("API_URL"):
        forced["api-server"] = config["API_URL"]
    return custom


# --------------------------------------------------------------------------
# Checked edits
# --------------------------------------------------------------------------


class Source:
    """A RustDesk checkout, edited with replacements that must match."""

    def __init__(self, root: Path, check_only: bool) -> None:
        self.root = root
        self.check_only = check_only
        self.changed: list[str] = []

    def replace(self, relative: str, old: str, new: str, count: int = 1) -> None:
        """Replace `old` with `new`; `old` must occur exactly `count` times."""
        path = self.root / relative
        if not path.is_file():
            raise ApplyError(f"{relative}: file not found in the RustDesk sources")
        text = path.read_text(encoding="utf-8")
        found = text.count(old)
        if found != count:
            raise ApplyError(
                f"{relative}: expected {count} occurrence(s) of {old!r}, found {found}. "
                "The RustDesk sources changed: scripts/apply.py needs an update."
            )
        self.write(relative, text.replace(old, new))

    def write(self, relative: str, content: str | bytes) -> None:
        self.changed.append(relative)
        if self.check_only:
            return
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")

    def git_apply(self, patch: Path) -> None:
        command = ["git", "-C", str(self.root), "apply", "--whitespace=nowarn"]
        if self.check_only:
            command.append("--check")
        result = subprocess.run(
            command + [str(patch.resolve())], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            raise ApplyError(f"patch {patch.name} does not apply:\n{result.stderr.strip()}")
        self.changed.append(f"patch {patch.name}")


# --------------------------------------------------------------------------
# Steps
# --------------------------------------------------------------------------


def apply_server(source: Source, config: dict[str, str]) -> None:
    """Make the instance server the built-in default, not only a setting."""
    host = config["SERVER_HOST"]
    source.replace("libs/hbb_common/src/config.rs", f'&["{UPSTREAM_SERVER}"]', f'&["{host}"]')
    source.replace("libs/hbb_common/src/config.rs", UPSTREAM_KEY, config["SERVER_KEY"])
    if config.get("API_URL"):
        source.replace(
            "src/common.rs",
            f'    "{UPSTREAM_API}".to_owned()\n',
            f'    "{config["API_URL"]}".to_owned()\n',
        )


def apply_custom_client(source: Source, custom: dict) -> None:
    """Compile the settings into the binary instead of reading custom.txt."""
    source.write("src/custom_client.json", json.dumps(custom, indent=2, sort_keys=True) + "\n")


def apply_names(source: Source, config: dict[str, str]) -> None:
    name = config["APP_NAME"]
    company = config["COMPANY"]
    bundle_id = config["BUNDLE_ID"]

    # Default name, used before the embedded settings are loaded.
    source.replace(
        "libs/hbb_common/src/config.rs",
        'RwLock::new("RustDesk".to_owned())',
        f'RwLock::new("{name}".to_owned())',
    )

    # Windows file properties. The upstream copyright notice is kept as is.
    for manifest in ("Cargo.toml", "libs/portable/Cargo.toml"):
        source.replace(manifest, 'ProductName = "RustDesk"', f'ProductName = "{name}"')
        source.replace(
            manifest,
            'FileDescription = "RustDesk Remote Desktop"',
            f'FileDescription = "{name}"',
        )
        source.replace(
            manifest, 'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{name}.exe"'
        )
    runner_rc = "flutter/windows/runner/Runner.rc"
    source.replace(
        runner_rc, 'VALUE "CompanyName", "Purslane Tech Pte. Ltd."', f'VALUE "CompanyName", "{company}"'
    )
    source.replace(
        runner_rc,
        'VALUE "FileDescription", "RustDesk Remote Desktop"',
        f'VALUE "FileDescription", "{name}"',
    )
    source.replace(
        runner_rc,
        'VALUE "OriginalFilename", "rustdesk.exe"',
        f'VALUE "OriginalFilename", "{name}.exe"',
    )
    source.replace(runner_rc, 'VALUE "ProductName", "RustDesk"', f'VALUE "ProductName", "{name}"')

    # macOS bundle.
    source.replace("Cargo.toml", 'name = "RustDesk"\nidentifier = "com.carriez.rustdesk"',
                   f'name = "{name}"\nidentifier = "{bundle_id}"')
    xcconfig = "flutter/macos/Runner/Configs/AppInfo.xcconfig"
    source.replace(xcconfig, "PRODUCT_NAME = RustDesk", f"PRODUCT_NAME = {name}")
    source.replace(
        xcconfig,
        "PRODUCT_BUNDLE_IDENTIFIER = com.carriez.flutterHbb",
        f"PRODUCT_BUNDLE_IDENTIFIER = {bundle_id}",
    )
    source.replace(
        "flutter/macos/Runner.xcodeproj/project.pbxproj",
        "PRODUCT_BUNDLE_IDENTIFIER = com.carriez.rustdesk;",
        f"PRODUCT_BUNDLE_IDENTIFIER = {bundle_id};",
        count=3,
    )
    source.replace(
        "flutter/macos/Runner/Info.plist",
        "<string>com.carriez.rustdesk</string>",
        f"<string>{bundle_id}</string>",
    )
    # build.py copies the service binary into the bundle by its upstream name.
    source.replace(
        "build.py",
        "./build/macos/Build/Products/Release/RustDesk.app/Contents/MacOS/')",
        f'"./build/macos/Build/Products/Release/{name}.app/Contents/MacOS/"\')',
    )

    # Linux desktop entry (the package and binary keep their upstream name).
    source.replace("res/rustdesk.desktop", "Name=RustDesk\n", f"Name={name}\n")


def apply_about(source: Source, config: dict[str, str]) -> None:
    """State that this is a modified build and where its source lives (AGPL)."""
    page = "flutter/lib/desktop/pages/desktop_setting_page.dart"
    website = config.get("WEBSITE_URL", "")
    source_url = config.get("SOURCE_URL", "")
    if website:
        source.replace(page, "launchUrlString('https://rustdesk.com');", f"launchUrlString('{website}');")
    notice = f"Built by {config['COMPANY']}. Modified version of RustDesk (AGPL-3.0)."
    if source_url:
        notice += f"\\nSource code: {source_url}"
    source.replace(
        page,
        "Purslane Tech Pte. Ltd.\\n$license',",
        f"Purslane Tech Pte. Ltd.\\n$license\\n{notice}',",
    )


def apply_accent(source: Source, config: dict[str, str]) -> None:
    accent = config.get("ACCENT_COLOR", "").lstrip("#").upper()
    if not accent or accent == UPSTREAM_ACCENT:
        return
    common = "flutter/lib/common.dart"
    source.replace(common, f"Color(0xFF{UPSTREAM_ACCENT})", f"Color(0xFF{accent})")
    source.replace(common, f"Color(0x77{UPSTREAM_ACCENT})", f"Color(0x77{accent})")
    source.replace(common, f"Color(0xAA{UPSTREAM_ACCENT})", f"Color(0xAA{accent})")
    source.replace(
        common,
        "static const Color button = Color(0xFF2C8CFF);",
        f"static const Color button = Color(0xFF{accent});",
    )


def apply_branding(source: Source, instance: Path) -> None:
    """Generate every icon RustDesk ships from `branding/icon.png`."""
    icon_path = instance / "branding" / "icon.png"
    logo_path = instance / "branding" / "logo.png"
    if not icon_path.is_file():
        raise ApplyError("branding/icon.png is missing (square PNG, 1024x1024 recommended)")
    try:
        from PIL import Image
    except ImportError as error:
        raise ApplyError("Pillow is required for the icons: pip install pillow") from error
    import io

    icon = Image.open(icon_path).convert("RGBA")
    if icon.width != icon.height or icon.width < 256:
        raise ApplyError("branding/icon.png must be square and at least 256x256")

    def png(size: int) -> bytes:
        buffer = io.BytesIO()
        icon.resize((size, size), Image.LANCZOS).save(buffer, format="PNG")
        return buffer.getvalue()

    def ico(sizes: list[int]) -> bytes:
        buffer = io.BytesIO()
        icon.save(buffer, format="ICO", sizes=[(size, size) for size in sizes])
        return buffer.getvalue()

    def icns() -> bytes:
        buffer = io.BytesIO()
        icon.resize((1024, 1024), Image.LANCZOS).save(buffer, format="ICNS")
        return buffer.getvalue()

    def svg(size: int) -> str:
        # An SVG wrapper keeps the upstream file names and loaders unchanged.
        data = base64.b64encode(png(size)).decode("ascii")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}"><image width="{size}" height="{size}" '
            f'xlink:href="data:image/png;base64,{data}"/></svg>\n'
        )

    full_ico = ico([16, 20, 24, 32, 40, 48, 64, 96, 128, 256])
    source.write("res/icon.ico", full_ico)
    source.write("flutter/windows/runner/resources/app_icon.ico", full_ico)
    source.write("res/tray-icon.ico", ico([16, 24, 32, 48]))
    source.write("res/icon.png", png(1024))
    source.write("res/mac-icon.png", png(1024))
    source.write("res/32x32.png", png(32))
    source.write("res/64x64.png", png(64))
    source.write("res/128x128.png", png(128))
    source.write("res/128x128@2x.png", png(256))
    source.write("res/scalable.svg", svg(256))
    source.write("flutter/macos/Runner/AppIcon.icns", icns())
    source.write("flutter/assets/icon.svg", svg(256))
    source.write("flutter/assets/icon.png", png(256))
    for size in (16, 32, 64, 128, 256, 512, 1024):
        asset = f"flutter/macos/Runner/Assets.xcassets/AppIcon.appiconset/app_icon_{size}.png"
        if (source.root / asset).is_file():
            source.write(asset, png(size))

    # Optional files, copied only when the instance provides them.
    if logo_path.is_file():
        source.write("flutter/assets/logo.png", logo_path.read_bytes())
    for name in ("logo_light.png", "logo_dark.png"):
        extra = instance / "branding" / name
        if extra.is_file():
            source.write(f"flutter/assets/{name}", extra.read_bytes())
    for name in ("mac-tray-dark-x2.png", "mac-tray-light-x2.png"):
        extra = instance / "branding" / name
        if extra.is_file():
            source.write(f"res/{name}", extra.read_bytes())


def apply_patches(source: Source, directory: Path) -> None:
    if not directory.is_dir():
        return
    for patch in sorted(directory.glob("*.patch")):
        source.git_apply(patch)


# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--instance", required=True, type=Path, help="instance directory")
    parser.add_argument("--source", type=Path, help="RustDesk checkout")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="only validate client.env and custom.json; no RustDesk checkout needed",
    )
    parser.add_argument(
        "--check", action="store_true", help="verify that everything applies, write nothing"
    )
    parser.add_argument(
        "--export-env",
        type=Path,
        help="append APP_NAME, APP_SLUG and APP_COMPANY to this file (GitHub Actions $GITHUB_ENV)",
    )
    args = parser.parse_args()

    if args.validate_only:
        try:
            config = read_env(args.instance / "client.env")
            validate(config)
            build_custom_client(args.instance, config)
        except ApplyError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        print(f"{config['APP_NAME']}: configuration is valid")
        return 0
    if args.source is None:
        parser.error("--source is required unless --validate-only is given")

    try:
        if not (args.source / "libs/hbb_common/src/config.rs").is_file():
            raise ApplyError(
                f"{args.source} is not a RustDesk checkout with its submodules "
                "(git submodule update --init --recursive)"
            )
        config = read_env(args.instance / "client.env")
        validate(config)
        custom = build_custom_client(args.instance, config)
        source = Source(args.source, args.check)

        apply_patches(source, GENERATOR_ROOT / "patches" / "core")
        apply_server(source, config)
        apply_custom_client(source, custom)
        apply_names(source, config)
        apply_about(source, config)
        apply_accent(source, config)
        apply_branding(source, args.instance)
        apply_patches(source, args.instance / "patches")
    except ApplyError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.export_env:
        slug = re.sub(r"[^a-z0-9]+", "-", config["APP_NAME"].lower()).strip("-")
        with args.export_env.open("a", encoding="utf-8") as env_file:
            env_file.write(f"APP_NAME={config['APP_NAME']}\n")
            env_file.write(f"APP_SLUG={slug}\n")
            env_file.write(f"APP_COMPANY={config['COMPANY']}\n")

    verb = "would change" if args.check else "changed"
    print(f"{config['APP_NAME']}: {verb} {len(source.changed)} item(s)")
    for item in source.changed:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
