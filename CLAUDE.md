# rustdesk-client

Open-source generator of branded RustDesk clients. `README.md` and `CONTRIBUTING.md` are the reference.

- Everything in this repository is written in **English**: code, comments, commit messages, documentation files.
  The wiki (`wiki/`) is bilingual: every page exists as `Page.md` and `Page-fr.md`, changed together.
- **Nothing specific to an organisation** may appear here (names, domains, keys, logos). Examples use `Example Org`
  and `rustdesk.example.com`. Organisation data lives in instance repositories.
- The repository is developed on Gitea and mirrored to GitHub (`sadjo/rustdesk-client`), where the builds, the wiki
  and the website run. Never push a tag without explicit approval: instances follow the moving tag `v1`.
- Every edit made to the RustDesk sources must be checked: `Source.replace` in `scripts/apply.py`, or a patch in
  `patches/core/`. No silent `sed`.
- Shell steps of `.github/workflows/build.yml` copied from RustDesk's `flutter-build.yml` stay verbatim, to keep
  upgrades a matter of diffing two upstream tags.
- Check before committing: `python3 scripts/apply.py --instance template --source <rustdesk checkout> --check`,
  `shellcheck scripts/*.sh`, `actionlint -shellcheck= .github/workflows/*.yml template/.github/workflows/build.yml`.
