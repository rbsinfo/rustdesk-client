[[Français|Troubleshooting-fr]]

# Troubleshooting

## Find the error

1. Open the failed run in the **Actions** tab of your instance repository.
2. Open the first job marked as failed.
3. Configuration errors are in the step **Apply the instance configuration**. They start with `error:`.

You can reproduce these errors on your machine in a few minutes. See "Check a configuration locally" in [[Configuration reference|Configuration-Reference]].

## Errors about client.env

| Message | Cause | Fix |
| --- | --- | --- |
| `missing configuration file: .../client.env` | No `client.env` at the root of the instance, or wrong `instance-path`. | Add the file, or fix `instance-path`. |
| `client.env:12: expected KEY=VALUE, got: ...` | A line is not `KEY=VALUE`. Keys are in upper case. `export KEY=...` is not accepted. | Fix the line. |
| `client.env:12: unknown key ...` | The key is not one of the nine known keys. | Remove it or fix the spelling. |
| `client.env: missing value for ...` | A required key is absent or empty. | Fill in `APP_NAME`, `COMPANY`, `BUNDLE_ID`, `SERVER_HOST` and `SERVER_KEY`. |
| `APP_NAME must be 1 to 40 characters among ...` | Unsupported character, such as an accent or an apostrophe, or a name that is too long. | Use ASCII letters, digits, space, dot, dash, underscore. |
| `APP_NAME must differ from 'RustDesk'` | The name is `RustDesk`. | Choose your own name. |
| `COMPANY contains unsupported characters` | Accent, apostrophe, parenthesis or another character outside the accepted set. | Use ASCII letters, digits, space, `.`, `,`, `&`, `-`, `_`. |
| `BUNDLE_ID must look like org.example.remotesupport` | Fewer than three parts, a part that starts with a digit, or an underscore. | Use three parts or more, letters first. |
| `SERVER_HOST must be a host name, optionally with :port` | A URL scheme, a path or a space in the value. | Write `rustdesk.example.com`, without `https://`. |
| `SERVER_KEY must be the server public key ...` | The value is not 44 base64 characters. Often a truncated copy or a missing final `=`. | Copy the content of `id_ed25519.pub` again. |
| `API_URL must be an http(s) URL` (also `WEBSITE_URL`, `SOURCE_URL`) | Missing `http://` or `https://`, or an unsupported character. | Write a full URL. |
| `ACCENT_COLOR must look like #1A2B3C` | Missing `#`, short form `#abc`, or a colour name. | Use six hexadecimal digits. |

## Errors about custom.json

| Message | Cause | Fix |
| --- | --- | --- |
| `custom.json is not valid JSON: ...` | Syntax error: trailing comma, comment, single quotes. | Validate the file: `python3 -m json.tool custom.json`. |
| `custom.json must contain a JSON object` | The file holds a list or a bare value. | Wrap the content in `{ }`. |
| `custom.json: override-settings must be an object` | The section is not `{ ... }`. | Fix the section. |
| `custom.json: override-settings.xyz must be a string` | A value is `true`, `false` or a number. | Write `"Y"`, `"N"` or `"123"`. |
| `custom.json: 'password' is not allowed ...` | `password` or `salt` at the top level. | Remove it. A password compiled into a public binary is not a secret. |

## Errors about branding

| Message | Fix |
| --- | --- |
| `branding/icon.png is missing (square PNG, 1024x1024 recommended)` | Add the file. The name is in lower case. |
| `branding/icon.png must be square and at least 256x256` | Export a square image of 1024x1024. |

## Errors about the RustDesk sources

| Message | Cause | Fix |
| --- | --- | --- |
| `...: expected 1 occurrence(s) of '...', found 0. The RustDesk sources changed: scripts/apply.py needs an update.` | `rustdesk-version` is not the tested version, and upstream changed that line. | Go back to the default version. See [Upgrading RustDesk](Upgrading-RustDesk). |
| `...: file not found in the RustDesk sources` | Same cause: a file moved upstream. | Same fix. |
| `patch ... does not apply:` | One of your patches does not match the sources. It may also touch a line that depends on `APP_NAME` or `ACCENT_COLOR`. | Redo the patch. See [Custom UI patches](Custom-UI-Patches). |
| `... is not a RustDesk checkout with its submodules` | Local run only: the clone has no submodules. | `git submodule update --init --recursive` |

## Workflow problems

| Symptom | Cause | Fix |
| --- | --- | --- |
| The workflow does not appear in the Actions tab. | `.github/` was not copied, or Actions is disabled for the repository. | Check that `.github/workflows/build.yml` exists. Enable Actions in **Settings > Actions**. |
| The run fails at once: the reusable workflow cannot be found. | Wrong ref after `@`, or your organisation restricts the actions and reusable workflows that may be used. | Check the ref. Allow `rbsinfo/rustdesk-client` and the actions it uses in the organisation settings. |
| Behaviour differs from this documentation. | The ref after `@` and `generator-ref` are different. | Make them identical. |
| No release after a build. | The run was started by hand, or the tag does not start with `v`, or a build job failed. | Push a tag such as `v1.0.0`. Fix the failed job. |
| The release step fails with a permission error. | `permissions: contents: write` is missing from the instance workflow. | Restore it from the template. |
| A platform was not built. | It is not in `targets`. | Use `windows`, `linux`, `macos`, separated by commas. |
| The macOS jobs fail in a signing step. | Some of the four `MACOS_*` secrets are missing or wrong. | See [Code signing](Code-Signing). |
| Actions minutes run out. | Private repository. macOS runners count ten times. | Build fewer platforms, or make the instance repository public. It holds no secret. |

## Client problems

| Symptom | Cause | Fix |
| --- | --- | --- |
| Windows shows "Windows protected your PC". | The binary is not code-signed yet. | **More info > Run anyway**. See [Code signing](Code-Signing). |
| macOS refuses to open the application. | Ad hoc signature. | **System Settings > Privacy & Security > Open Anyway**. |
| macOS asks for Screen Recording or Accessibility again after an update. | Ad hoc signature: each build is a different application for macOS. | Grant again, or sign with a Developer ID. |
| The Linux package refuses to install or replaces RustDesk. | The package keeps the name `rustdesk`. | Remove the official package first. The two cannot coexist. |
| The client never becomes ready. | `SERVER_HOST` does not resolve, or ports 21115 to 21117 are blocked. | See [Server setup](Server-Setup). |
| Connections fail with a key error. | `SERVER_KEY` is not the key of that server, or the technician's client uses another key. | Compare with `id_ed25519.pub`. Rebuild if it was wrong. |
| The client still shows the old server after a rebuild. | An old version is still installed. | Uninstall it, then install the new build. |
| The user cannot connect to another device. | `"conn-type": "incoming"` is set. | This is the intended behaviour of the template. Remove the key for a technician client. |
| The device does not appear in the console. | `API_URL` is empty or wrong, or you run the OSS server only. | Set `API_URL`. Check that the URL opens from the device. |
| All devices look the same in the console. | The client does not send the application name. | Group devices on the server side. |
| A setting from `custom.json` has no effect. | Misspelt name, or the setting is in the wrong section. | Check the name and the section in [Configuration reference](Configuration-Reference). |
| The RustDesk logo is still visible somewhere. | An optional logo file is not provided, or the screen draws it another way. | Add the files listed in [Branding](Branding), or write a patch. |

## Ask for help

Open an issue on the generator repository with:

- the generator ref and the RustDesk version,
- the name of the failed job and step,
- the full `error:` message,
- your `client.env` and `custom.json`. They hold no secret.

Problems with RustDesk itself, unrelated to the branding, belong to the RustDesk project. Reproduce them with an official client first.
