[[Français|Home-fr]]

# rustdesk-client

`rustdesk-client` builds a branded, preconfigured RustDesk remote-support client for Windows, macOS and Linux with GitHub Actions. It replaces third-party client generators: the build runs in your own GitHub repository, from the official RustDesk sources.

> This project is not affiliated with RustDesk or Purslane. "RustDesk" is a trademark of its owner. The clients you build are modified versions of RustDesk, distributed under the AGPL-3.0.

## How it works

There are two repositories.

| Repository | Owner | Content |
| --- | --- | --- |
| Generator (`rbsinfo/rustdesk-client`) | This project | `scripts/apply.py`, the reusable build workflow, the instance template. Nothing organisation-specific. |
| Instance | You | Your application name, server address, server public key, icons and optional patches, plus a short workflow that calls the generator. |

The instance workflow calls the generator at a fixed ref:

```yaml
jobs:
  build:
    uses: rbsinfo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
```

You do not fork anything. To move to a newer generator, change `@v1` and `generator-ref`.

For each platform, the build:

1. Checks out the official RustDesk sources at the pinned tag (default `1.5.3`).
2. Runs `scripts/apply.py`, which applies your configuration to those sources. Every edit is checked. If the RustDesk sources changed and a pattern no longer matches, the build stops with an error.
3. Compiles the client and uploads the binaries, together with an archive of the modified sources.

## What you get

- A client that carries your name, icon and accent colour.
- Your server host and public key compiled into the binary. Users have nothing to type.
- Settings compiled into the binary from `custom.json`, for example incoming connections only.
- A client that runs without installation for a one-off session, and that can be installed as a service for unattended access.
- With an API server (RustDesk Server Pro or a compatible console), devices that appear in the console with their ID, host name, user name, OS and version.

## Pages

| Page | Read it when |
| --- | --- |
| [Quick start](Quick-Start) | You want a first build. |
| [Configuration reference](Configuration-Reference) | You edit `client.env` or `custom.json`. |
| [Branding](Branding) | You prepare icons and logos. |
| [Custom UI patches](Custom-UI-Patches) | You need to change the interface beyond name, icons and colour. |
| [Building and releasing](Building-and-Releasing) | You want the workflow inputs, the artifact names, or to publish a release. |
| [Code signing](Code-Signing) | You want to sign and notarise the macOS application, or understand the Windows warning. |
| [Server setup](Server-Setup) | You need to know what the client expects from your server. |
| [Upgrading RustDesk](Upgrading-RustDesk) | You change the RustDesk version. |
| [Troubleshooting](Troubleshooting) | A build or a client does not behave as expected. |
| [License and AGPL](License-and-AGPL) | You distribute the client. |

## Known limitations

- Windows x86_64, macOS x86_64 and Apple Silicon, Linux x86_64 only. No Android, no iOS.
- The Linux package and binary keep the upstream name `rustdesk`. The package cannot be installed next to the official RustDesk package.
- Windows binaries are not code-signed yet. SmartScreen shows a warning. Signing integration is planned.
- macOS applications are ad hoc signed unless you provide a Developer ID certificate. See [Code signing](Code-Signing).
- The privacy-screen image cannot be customised yet.
- Only the default RustDesk version is tested.
