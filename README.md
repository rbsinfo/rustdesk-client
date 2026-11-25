# rustdesk-client

Build your own branded, preconfigured [RustDesk](https://github.com/rustdesk/rustdesk)
remote support client for Windows, macOS and Linux, with GitHub Actions.

[Website](https://rbsinfo.github.io/rustdesk-client/) ·
[Documentation](https://github.com/rbsinfo/rustdesk-client/wiki) ·
[Documentation en français](https://github.com/rbsinfo/rustdesk-client/wiki/Home-fr)

> This project is not affiliated with, endorsed by or sponsored by RustDesk or
> Purslane Tech Pte. Ltd. "RustDesk" is a trademark of its owner.

## What it does

You keep a small repository of your own (an *instance*) with your name, your
server address and public key, your icon and, if you want, patches for the
interface. Its workflow calls this project, which:

1. checks out the official RustDesk sources at a pinned version;
2. applies your configuration with `scripts/apply.py`, which stops on the first
   edit that does not match the sources;
3. builds the client on GitHub-hosted runners;
4. optionally publishes a release with the binaries, their checksums and the
   modified sources.

The settings are compiled into the binary. A typical use is an
*incoming only* client: your customers run it, you connect to them, and it
cannot be used to reach other machines.

| Platform | Output |
| --- | --- |
| Windows x86_64 | portable `.exe`, `.msi` |
| macOS x86_64 and Apple Silicon | `.dmg` |
| Linux x86_64 | `.deb`, `.rpm` |

## Quick start

```sh
git clone https://github.com/rbsinfo/rustdesk-client.git
cd rustdesk-client
scripts/new-instance.sh my-org/my-support-client
```

The script asks for the application name, your server host and its public key,
creates the repository from [`template/`](template/) and tells you how to start
the first build. The [quick start](https://github.com/rbsinfo/rustdesk-client/wiki/Quick-Start)
covers the manual path as well.

An instance is five files:

```text
client.env                     name, publisher, server, public key
custom.json                    client settings (incoming only, enforced options)
branding/icon.png              application icon
patches/                       optional patches for the RustDesk sources
.github/workflows/build.yml    ten lines calling this project
```

## Status

The generator targets RustDesk 1.5.3. Known limitations:

- Windows binaries are not code-signed yet; macOS builds are ad hoc signed
  unless you provide a Developer ID certificate.
- The Linux package and binary keep the upstream name `rustdesk`.
- No Android or iOS build.

## Repository layout

| Path | Purpose |
| --- | --- |
| `scripts/apply.py` | Applies an instance to a RustDesk checkout |
| `scripts/new-instance.sh` | Creates an instance repository |
| `patches/core/` | Patches every client gets |
| `template/` | Starting point of an instance, also used by the self-test |
| `.github/workflows/build.yml` | Reusable build workflow |
| `wiki/` | Sources of the GitHub wiki (English and French) |
| `site/` | Sources of the website |

## License

[AGPL-3.0](LICENSE), like RustDesk. A client built with this project is a
modified version of RustDesk: if you distribute it, you must offer its complete
corresponding source. Releases made by the build workflow attach it. See
[License and AGPL](https://github.com/rbsinfo/rustdesk-client/wiki/License-and-AGPL).
