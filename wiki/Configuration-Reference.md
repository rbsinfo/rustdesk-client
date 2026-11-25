[[Français|Configuration-Reference-fr]]

# Configuration reference

An instance is configured by two files at its root:

| File | Role |
| --- | --- |
| `client.env` | Identity of the client and address of the server. |
| `custom.json` | RustDesk settings compiled into the client. |

Both are read by `scripts/apply.py` at build time. Neither holds a secret: everything in them can be read from the client you distribute.

## client.env

### Format

- One `KEY=VALUE` per line. The file is parsed, never executed.
- Empty lines and lines starting with `#` are ignored.
- A value may be wrapped in single or double quotes. The quotes are removed.
- A comment at the end of a line is not supported: it would become part of the value.
- An unknown key stops the build.

### Keys

| Key | Required | Rules | Example |
| --- | --- | --- | --- |
| `APP_NAME` | yes | 1 to 40 characters among letters, digits, space, dot, dash and underscore. Starts with a letter or a digit. Does not end with a space. Must not be `RustDesk`, in any case. | `Remote Support` |
| `COMPANY` | yes | 1 to 80 characters among letters, digits, space, dot, comma, `&`, dash and underscore. Starts with a letter or a digit. | `Example Org` |
| `BUNDLE_ID` | yes | Reverse-DNS identifier with at least three parts. Each part starts with a letter and holds letters, digits and dashes. | `org.example.remotesupport` |
| `SERVER_HOST` | yes | Host name or IP address of your `hbbs` server. Add `:port` only when the port is not 21116. | `rustdesk.example.com` |
| `SERVER_KEY` | yes | Public key of the server: the content of `id_ed25519.pub`. 44 base64 characters that decode to 32 bytes. | `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=` |
| `API_URL` | no | `http://` or `https://` URL of the API server or web console. Leave empty when you only run `hbbs` and `hbbr`. | `https://rustdesk.example.com` |
| `WEBSITE_URL` | no | `http://` or `https://` URL opened by the website link of the About page. | `https://www.example.com` |
| `SOURCE_URL` | no, recommended | `http://` or `https://` URL where the source of your client is published. Shown on the About page. | `https://github.com/example-org/remote-support` |
| `ACCENT_COLOR` | no | Accent colour of the interface, as `#RRGGBB`. | `#1A2B3C` |

Letters are ASCII letters, without accents.

### What each key changes

| Key | Effect |
| --- | --- |
| `APP_NAME` | Name shown to users, Windows executable name and file properties, macOS bundle name, name of the Linux desktop entry. A lower-case form with dashes (`remote-support`) prefixes the artifact file names. |
| `COMPANY` | Publisher in the Windows file properties and in the MSI. Named in the About page notice. |
| `BUNDLE_ID` | Identifier of the macOS application. |
| `SERVER_HOST`, `SERVER_KEY` | Forced as `custom-rendezvous-server` and `key` in `override-settings`. They also replace the default server and key built into RustDesk. |
| `API_URL` | When set: forced as `api-server` in `override-settings`, and replaces the built-in default API address. |
| `WEBSITE_URL` | When set: target of the website link on the About page. |
| `SOURCE_URL` | When set: added to the About page as `Source code: <url>`. |
| `ACCENT_COLOR` | When set: replaces the accent colour of the RustDesk interface. |

The About page always states: `Built by <COMPANY>. Modified version of RustDesk (AGPL-3.0).` The upstream copyright notice is kept.

### Example

```ini
# Name shown to users.
APP_NAME=Remote Support

# Publisher.
COMPANY=Example Org

# macOS identifier.
BUNDLE_ID=org.example.remotesupport

# Server and its public key.
SERVER_HOST=rustdesk.example.com
SERVER_KEY=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=

# Optional.
API_URL=https://rustdesk.example.com
WEBSITE_URL=https://www.example.com
SOURCE_URL=https://github.com/example-org/remote-support
ACCENT_COLOR=#1A2B3C
```

## custom.json

RustDesk normally reads custom-client settings from a `custom.txt` file signed with a key held by RustDesk. This generator compiles the settings into the binary instead. No file next to the executable can change them.

### Structure

```json
{
  "conn-type": "incoming",
  "override-settings": {
    "hide-powered-by-me": "Y",
    "allow-auto-update": "N",
    "verification-method": "use-both-passwords"
  },
  "default-settings": {}
}
```

| Section | Meaning |
| --- | --- |
| `override-settings` | Settings imposed on the client. The user cannot change them. |
| `default-settings` | Initial values. The user can change them. |
| Any other top-level key | A hard setting, fixed for the whole client. |
| `app-name` | Written by the build from `APP_NAME`. A value set here is replaced. |

### Rules checked at build time

- The file must be a JSON object.
- `override-settings` and `default-settings` must be objects. A missing section is treated as empty.
- Every value inside these two sections must be a string: write `"Y"`, not `true`.
- The top-level keys `password` and `salt` are refused. The binary is public, so a preset password would be readable by anyone holding the client.
- `custom-rendezvous-server`, `key` and `api-server` in `override-settings` are always overwritten by `client.env`.

The file is optional. Without it, the client only receives the server settings from `client.env`.

### Hard settings (top level)

| Key | Value | Effect |
| --- | --- | --- |
| `conn-type` | `"incoming"` | Incoming connections only. The client can be controlled but cannot connect to other devices. |
| `disable-settings` | `"Y"` | The user cannot open the settings. |
| `disable-installation` | `"Y"` | The client cannot be installed. It only runs as a one-off session. |
| `disable-ab` | `"Y"` | No address book. |
| `disable-account` | `"Y"` | No account login. |
| `disable-tcp-listen` | `"Y"` | The client does not listen for direct TCP connections. |

### Settings for `override-settings` or `default-settings`

| Key | Values | Effect |
| --- | --- | --- |
| `approve-mode` | `password`, `click`, or empty | How an incoming session is accepted: by password, by a click from the user, or either one when empty. |
| `verification-method` | `use-temporary-password`, `use-permanent-password`, `use-both-passwords` | Which passwords are accepted. |
| `hide-powered-by-me` | `Y` | Set in the template. Hides the "Powered by RustDesk" mention. |
| `allow-auto-update` | `N` | Set in the template. Automatic updates stay off. |

`apply.py` checks the structure of the file, not the names of the settings. A misspelt name is compiled in and silently ignored by the client. Check the result on a test machine.

Update checks against upstream are already disabled for custom clients: RustDesk does this itself when the application name is not `RustDesk`.

### Examples

Attended support only. The user accepts each session by a click, and the client cannot be installed:

```json
{
  "conn-type": "incoming",
  "disable-installation": "Y",
  "override-settings": {
    "approve-mode": "click"
  },
  "default-settings": {}
}
```

Unattended access with a permanent password that each user sets after installation:

```json
{
  "conn-type": "incoming",
  "override-settings": {
    "approve-mode": "password",
    "verification-method": "use-permanent-password"
  },
  "default-settings": {}
}
```

### What is compiled in

With the `client.env` example above and the template `custom.json`, the build embeds:

```json
{
  "app-name": "Remote Support",
  "conn-type": "incoming",
  "default-settings": {},
  "override-settings": {
    "allow-auto-update": "N",
    "api-server": "https://rustdesk.example.com",
    "custom-rendezvous-server": "rustdesk.example.com",
    "hide-powered-by-me": "Y",
    "key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    "verification-method": "use-both-passwords"
  }
}
```

## Check a configuration locally

You can validate an instance without waiting for a full build. You need Python 3 with Pillow, and `git`.

```sh
git clone --branch 1.5.3 --recurse-submodules https://github.com/rustdesk/rustdesk
git clone https://github.com/rbsinfo/rustdesk-client
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance path/to/instance --source rustdesk --check
```

`--check` verifies that everything applies and writes nothing.
