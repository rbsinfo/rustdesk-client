[[Français|Building-and-Releasing-fr]]

# Building and releasing

## The instance workflow

Your instance repository holds one workflow, `.github/workflows/build.yml`. It calls the reusable workflow of the generator.

```yaml
name: Build client

on:
  workflow_dispatch:
    inputs:
      targets:
        description: Platforms to build (windows, linux, macos)
        default: "windows,linux,macos"
  push:
    tags: ["v*"]

permissions:
  contents: write

jobs:
  build:
    # Keep the ref after "@" and `generator-ref` identical.
    uses: sadjo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
      targets: ${{ inputs.targets || 'windows,linux,macos' }}
      release-tag: ${{ startsWith(github.ref, 'refs/tags/') && github.ref_name || '' }}
    secrets: inherit
```

Two triggers:

| Trigger | Result |
| --- | --- |
| Manual run (**Actions > Build client > Run workflow**) | Test binaries, kept as artifacts of the run. No release. |
| Push of a tag that starts with `v` | All platforms are built and a GitHub release is published with that tag. |

## Inputs of the reusable workflow

| Input | Default | Meaning |
| --- | --- | --- |
| `rustdesk-version` | `"1.5.3"` | RustDesk tag to build. Only the default is tested. |
| `targets` | `"windows,linux,macos"` | Comma-separated list among `windows`, `linux`, `macos`. |
| `instance-path` | `"."` | Directory of the instance inside the calling repository. |
| `release-tag` | `""` | When set, the binaries are published as a GitHub release with this tag. |
| `generator-repository` | `"sadjo/rustdesk-client"` | Repository that provides `scripts/apply.py`. Change it only when you call a fork. |
| `generator-ref` | `"v1"` | Ref of the generator. Keep it equal to the ref after `@` in `uses:`. |

The ref after `@` selects the workflow file. `generator-ref` selects the scripts and patches. If they differ, the workflow and the scripts may not match.

## Secrets

All secrets are optional. They only concern macOS signing. See [[Code signing|Code-Signing]].

| Secret | Content |
| --- | --- |
| `MACOS_P12_BASE64` | Developer ID certificate (`.p12`), base64-encoded |
| `MACOS_P12_PASSWORD` | Password of the `.p12` file |
| `MACOS_CODESIGN_IDENTITY` | Signing identity |
| `MACOS_NOTARIZE_JSON` | App Store Connect API key for `rcodesign`, base64-encoded |

`secrets: inherit` passes the secrets of your repository to the generator workflow.

## Jobs

| Job | Runner | Runs when |
| --- | --- | --- |
| `bridge` | `ubuntu-22.04` | Always. Generates the Dart/Rust bridge and archives the modified sources. |
| `windows privacy window` | `windows-2022` | `targets` contains `windows` |
| `windows x86_64` | `windows-2022` | `targets` contains `windows` |
| `macos x86_64` | `macos-15-intel` | `targets` contains `macos` |
| `macos aarch64` | `macos-15` | `targets` contains `macos` |
| `linux x86_64` | `ubuntu-22.04` | `targets` contains `linux` |
| `release` | `ubuntu-22.04` | `release-tag` is set and no job failed or was cancelled |

Each build job checks out RustDesk at the requested tag, the generator, and your instance, then runs `scripts/apply.py` before compiling.

Builds run on GitHub-hosted runners and take about 30 to 60 minutes.

## Files produced

`<slug>` is `APP_NAME` in lower case with dashes: `Remote Support` gives `remote-support`. `<version>` is the RustDesk version, for example `1.5.3`.

| File | Platform | Content |
| --- | --- | --- |
| `<slug>-<version>-windows-x86_64.exe` | Windows x86_64 | Self-extracting executable. Runs without installation and can install the client. |
| `<slug>-<version>-windows-x86_64.msi` | Windows x86_64 | MSI package, for deployment tools. |
| `<slug>-<version>-macos-x86_64.dmg` | macOS, Intel | Disk image. |
| `<slug>-<version>-macos-aarch64.dmg` | macOS, Apple Silicon | Disk image. |
| `<slug>-<version>-linux-x86_64.deb` | Linux x86_64 | Debian/Ubuntu package. |
| `<slug>-<version>-linux-x86_64.rpm` | Linux x86_64 | RPM package. |
| `<slug>-<version>-source.tar.gz` | all | The RustDesk sources as modified for your client. |
| `SHA256SUMS` | all | Checksums of the files above. Releases only. |

On a manual run, the files are grouped in these artifacts:

| Artifact | Content |
| --- | --- |
| `client-windows-x86_64` | `.exe` and `.msi` |
| `client-macos-x86_64` | `.dmg` |
| `client-macos-aarch64` | `.dmg` |
| `client-linux-x86_64` | `.deb` and `.rpm` |
| `client-source` | `-source.tar.gz` |

The other artifacts of a run (`bridge-artifact`, `bridge-artifact-flutter-3.44`, `topmostwindow-artifacts-x64`) are intermediate build files.

## Build by hand

From the Actions tab, or with the GitHub CLI:

```sh
gh workflow run "Build client" -f targets=windows
gh run watch
gh run download --name client-windows-x86_64
```

## Publish a release

```sh
git tag v1.0.0
git push origin v1.0.0
```

The release is created in your instance repository with:

- all the binaries,
- the source archive,
- `SHA256SUMS`,
- a description that names the RustDesk version, the commit of your configuration, and the licence.

The tag is your own version number. It names the release, not the files: file names carry the RustDesk version. Two releases built from the same RustDesk version have files with the same names.

Users can check a download:

```sh
sha256sum --check --ignore-missing SHA256SUMS
```

## Cost

- Public instance repository: GitHub-hosted runners are free.
- Private instance repository: builds consume your Actions minutes. macOS runners count ten times. Build only the platforms you need with `targets`.

## Pin the generator

`@v1` follows the `v1` line of the generator. For a build that does not change until you decide so, use a full commit SHA of the generator in both places:

```yaml
    uses: sadjo/rustdesk-client/.github/workflows/build.yml@0123456789abcdef0123456789abcdef01234567
    with:
      generator-ref: 0123456789abcdef0123456789abcdef01234567
```

## Several clients

Create one instance repository per client. It keeps the releases, the tags and the published source of each client separate.
