[[Français|Custom-UI-Patches-fr]]

# Custom UI patches

`client.env`, `custom.json` and `branding/` cover the name, the icons, the accent colour and the settings. For anything else, such as hiding a button, rewording a label or changing a screen, you write patches against the RustDesk sources.

RustDesk's core is written in Rust (`src/`, `libs/`). Its interface is written in Flutter/Dart (`flutter/lib/`).

## How patches are applied

- Put `*.patch` files in the `patches/` directory of your instance.
- They are applied with `git apply`, in alphabetical order of file name.
- They are applied last: after the generator's own patch, the server, names, About page, accent colour and icons.
- Only files directly in `patches/` with the `.patch` extension are read.
- A patch that does not apply stops the build with an error that names the patch.

Because your patches come last, write them against sources that have already been through `apply.py`.

## Write a patch

### 1. Get the sources at the version you build

Use the value of `rustdesk-version` in your `.github/workflows/build.yml`.

```sh
git clone --branch 1.5.3 --recurse-submodules https://github.com/rustdesk/rustdesk
git clone https://github.com/sadjo/rustdesk-client
```

### 2. Apply your configuration and commit

```sh
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance path/to/instance --source rustdesk
git -C rustdesk add -A
git -C rustdesk commit -m "Instance configuration applied"
```

This commit is your baseline. It stays on your machine.

If your instance already has patches, they are applied at this step and are part of the baseline.

### 3. Make the change

Edit the files in `rustdesk/`. Keep the change small and local: a short patch survives upgrades better.

### 4. Export the patch

```sh
git -C rustdesk diff > path/to/instance/patches/0001-hide-something.patch
```

Number the files (`0001-`, `0002-`) to control the order.

Two things `git diff` leaves out:

- A file you created. Declare it first with `git -C rustdesk add -N path/to/new_file`.
- A change inside a submodule, such as `libs/hbb_common`. Keep your patches to files of the main RustDesk repository.

To add another patch, commit the previous change in `rustdesk/` first, so that the next `git diff` only holds the new change.

### 5. Verify

Run the check on a clean checkout:

```sh
git -C rustdesk reset --hard
git -C rustdesk checkout 1.5.3
git -C rustdesk submodule update --init --recursive
python3 rustdesk-client/scripts/apply.py --instance path/to/instance --source rustdesk --check
```

The output lists each item that would change, including `patch 0001-hide-something.patch`.

Then commit the patch in your instance repository and run the build.

## Advice

- One purpose per patch. A patch that fails is then easy to identify and to redo.
- Avoid lines that `apply.py` rewrites, such as the application name or the accent colour. A patch whose context contains your `APP_NAME` stops applying when you rename the client.
- Do not use a patch for something `custom.json` can do. Settings survive upgrades. Patches may not.
- A patch that compiles is not a patch that works. Test the client on each platform you distribute.
- Your patches are part of the source you must publish. See [[License and AGPL|License-and-AGPL]].

## After a RustDesk upgrade

A patch written for one RustDesk version may not apply to the next. The build then stops:

```text
error: patch 0001-hide-something.patch does not apply:
error: patch failed: flutter/lib/desktop/pages/connection_page.dart:120
```

Redo the patch against the new version with the steps above. See [[Upgrading RustDesk|Upgrading-RustDesk]].
