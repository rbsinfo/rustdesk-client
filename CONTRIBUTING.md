# Contributing

Thank you for helping. Issues and pull requests are welcome on
[GitHub](https://github.com/sadjo/rustdesk-client).

## Ground rules

- Code, comments, commit messages and files in this repository are in English.
  The wiki exists in English and French: change both versions of a page
  together (`Page.md` and `Page-fr.md`).
- Nothing specific to one organisation belongs here. Names, servers, keys and
  logos live in instance repositories; examples use `Example Org` and
  `rustdesk.example.com`.
- Every edit `scripts/apply.py` makes to the RustDesk sources must be checked:
  use `Source.replace`, which fails when the pattern is not found, or a patch
  in `patches/core/`.

## Checking a change locally

```sh
git clone --depth 1 --branch 1.5.3 --recurse-submodules --shallow-submodules \
  https://github.com/rustdesk/rustdesk.git /tmp/rustdesk
python3 -m pip install pillow
python3 scripts/apply.py --instance template --source /tmp/rustdesk --check
shellcheck scripts/*.sh
```

A full build cannot run on your machine in reasonable time. Run the
**Self-test** workflow on your fork (Actions tab) for the platforms you touched
and link the run in the pull request.

## Supporting a new RustDesk version

1. Diff `.github/workflows/flutter-build.yml` and `bridge.yml` of RustDesk
   between the current and the new tag, and port the relevant changes to
   `.github/workflows/build.yml`.
2. Run `scripts/apply.py --check` against the new tag and fix what no longer
   matches.
3. Update the default version in `build.yml`, `ci.yml`, `selftest.yml`,
   `template/.github/workflows/build.yml` and the documentation.
4. Run the self-test for every platform.
