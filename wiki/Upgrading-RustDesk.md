[[Français|Upgrading-RustDesk-fr]]

# Upgrading RustDesk

A client is built from the official RustDesk sources at a pinned tag. The default is `1.5.3`. Nothing changes until you change it.

There are two version numbers in your instance workflow:

```yaml
    uses: sadjo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
```

| Value | What it selects |
| --- | --- |
| `@v1` and `generator-ref` | The version of the generator: workflow, `apply.py`, core patch. |
| `rustdesk-version` | The RustDesk tag that is compiled. |

Only the default RustDesk version of a generator release is tested. Other versions may work. Nothing guarantees it.

## Recommended: follow the generator

1. Wait for a generator release that raises the default RustDesk version.
2. Read its release notes.
3. Update `@<ref>` and `generator-ref` if the release asks for it. Keep the two identical.
4. Set `rustdesk-version` to the new default.
5. Run a manual build and test the client before you tag a release.

## Trying a newer RustDesk version yourself

Change one line:

```yaml
      rustdesk-version: "1.5.4"
```

Check locally first. It takes a few minutes instead of a full build.

```sh
git clone --branch 1.5.4 --recurse-submodules https://github.com/rustdesk/rustdesk rustdesk-1.5.4
git clone https://github.com/sadjo/rustdesk-client
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance path/to/instance --source rustdesk-1.5.4 --check
```

`--check` writes nothing. It ends with the list of items that would change, or with an error.

## What can fail

### A pattern of apply.py no longer matches

`apply.py` edits the RustDesk sources by exact replacement. Each pattern must be found the expected number of times. If upstream changed the line, the script stops and names the file and the pattern:

```text
error: flutter/lib/common.dart: expected 1 occurrence(s) of 'Color(0xFF0071FF)', found 0. The RustDesk sources changed: scripts/apply.py needs an update.
```

This is intended. A build that stops is better than a client that is half branded or that points to the wrong server.

What to do: stay on the tested version, and open an issue on the generator with the RustDesk version and the full message.

### The core patch no longer applies

The generator applies its own patch, `patches/core/0001-embedded-custom-client.patch`, which compiles the settings into the binary.

```text
error: patch 0001-embedded-custom-client.patch does not apply:
```

Same answer: stay on the tested version and report it.

### One of your patches no longer applies

```text
error: patch 0001-hide-something.patch does not apply:
```

The message names a file from your `patches/` directory. Redo that patch against the new version. See [[Custom UI patches|Custom-UI-Patches]].

### The compilation fails

The reusable workflow installs a toolchain (Rust, Flutter, vcpkg and others) chosen for the default RustDesk version. A newer RustDesk version may need a newer toolchain. `apply.py` then succeeds and the compilation fails later.

This cannot be fixed from an instance. Wait for a generator release that supports the version.

## After an upgrade

1. Run a manual build for every platform you distribute.
2. Test on real machines: one-off session, installation, unattended access, your patched screens.
3. On macOS with an ad hoc signature, grant Screen Recording and Accessibility again. See [[Code signing|Code-Signing]].
4. Tag a new release. Each release carries its own source archive, so the published source follows the upgrade.

## Going back

The configuration lives in Git. Revert the commit that changed `rustdesk-version` and build again.

Custom clients do not check for updates against upstream. Users get a new version only when you distribute it.
