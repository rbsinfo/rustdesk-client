[[Français|Quick-Start-fr]]

# Quick start

This page takes you from nothing to a first build. Builds run on GitHub-hosted runners and take about 30 to 60 minutes.

## Before you start

You need:

- A GitHub account. An organisation account works the same way.
- A running RustDesk server: its host name and its public key (the content of `id_ed25519.pub`). See [[Server setup|Server-Setup]].
- A square PNG icon, 1024x1024 recommended.
- For the script path only: `git` and the GitHub CLI `gh`, logged in (`gh auth login`).

Nothing in an instance repository is secret. The server address and the public key can be read from any client you distribute. A public repository gets free GitHub-hosted runners. A private repository consumes Actions minutes, and macOS runners count ten times.

## Path A: the script

Clone the generator and run the script with the name of the repository to create.

```sh
git clone https://github.com/rbsinfo/rustdesk-client
cd rustdesk-client
scripts/new-instance.sh example-org/remote-support --private
```

Leave out `--private` to create a public repository.

The script asks for:

| Question | Example |
| --- | --- |
| Application name | `Remote Support` |
| Company | `Example Org` |
| Bundle identifier | `org.example.remotesupport` |
| Server host | `rustdesk.example.com` |
| Server public key | content of `id_ed25519.pub` |
| API URL (optional) | `https://rustdesk.example.com` |

It then creates the GitHub repository from `template/` and prints the next steps.

## Path B: by hand

Copy the template into a new repository.

```sh
git clone https://github.com/rbsinfo/rustdesk-client
mkdir remote-support
cp -R rustdesk-client/template/. remote-support/
cd remote-support
git init -b main
```

The trailing `/.` matters: it also copies `.github/` and `.gitignore`.

Edit `client.env`:

```ini
APP_NAME=Remote Support
COMPANY=Example Org
BUNDLE_ID=org.example.remotesupport
SERVER_HOST=rustdesk.example.com
SERVER_KEY=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
API_URL=
WEBSITE_URL=
SOURCE_URL=https://github.com/example-org/remote-support
ACCENT_COLOR=
```

Then commit and push:

```sh
git add -A
git commit -m "Initial configuration"
gh repo create example-org/remote-support --private --source . --push
```

## Then, for both paths

1. Replace `branding/icon.png` with your icon. See [[Branding|Branding]].
2. Review `custom.json`. The template builds an incoming-only client: it can be controlled but cannot connect to other devices. See [[Configuration reference|Configuration-Reference]].
3. Set `SOURCE_URL` in `client.env` to the place where the source of your client is published. See [[License and AGPL|License-and-AGPL]].
4. Commit and push.

## First build

In your instance repository on GitHub: **Actions > Build client > Run workflow**.

Or from a terminal:

```sh
gh workflow run "Build client" -f targets=windows
```

Building one platform first is quicker when you only want to check the configuration. When the run ends, download the binaries from the **Artifacts** section of the run page.

## First release

Push a tag that starts with `v`:

```sh
git tag v1.0.0
git push origin v1.0.0
```

The workflow builds every platform and publishes a GitHub release with the binaries, `SHA256SUMS` and the source archive. See [[Building and releasing|Building-and-Releasing]].

## Check the client

1. Start the client on a test machine. It shows your name and icon.
2. The status line at the bottom of the window reports that the client is ready. If not, see [[Troubleshooting|Troubleshooting]].
3. Connect to its ID from a standard RustDesk client configured for the same server.
4. If you set `API_URL`, check that the device appears in your console.
