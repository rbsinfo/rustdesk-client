[[Français|Code-Signing-fr]]

# Code signing

| Platform | Default | With your certificate |
| --- | --- | --- |
| Windows | Not signed. SmartScreen warns. | Not integrated yet. Planned. |
| macOS | Ad hoc signature. Gatekeeper blocks the first launch. | Developer ID signature and notarisation, with four secrets. |
| Linux | Packages are not signed. | Not integrated. |

Every release includes `SHA256SUMS`, so users can at least verify the integrity of a download.

## Windows

The `.exe` and `.msi` files are not code-signed yet. On first launch, Windows SmartScreen may show "Windows protected your PC".

What users do: **More info > Run anyway**.

What you can do for now:

- Tell your users to expect the warning, and publish the checksum next to the download link.
- Deploy the `.msi` with your management tool rather than asking users to download it.
- Sign the downloaded files yourself with your own certificate and `signtool`. The files packed inside the self-extracting executable stay unsigned, and the checksums in `SHA256SUMS` no longer match the signed files.

Signing in the workflow is planned.

## macOS without a certificate

Without secrets, the application gets an ad hoc signature. It runs, but macOS does not know its publisher.

First launch:

1. Open the disk image and drag the application to **Applications**.
2. Open the application. macOS refuses.
3. Open **System Settings > Privacy & Security**, scroll to the message about the application, and click **Open Anyway**.

Permissions:

1. On first use, grant **Screen Recording** and **Accessibility** in **System Settings > Privacy & Security**.
2. After each update of the client, grant them again. An ad hoc signature changes with every build, so macOS treats the update as a different application. If the switches look enabled but the client still asks, remove the entry from the list and add it again.

This is acceptable for a few managed machines. For wider distribution, sign with a Developer ID.

## macOS with a Developer ID

You need a paid Apple Developer Program membership.

The workflow then signs the application with your identity, builds the disk image, signs it, submits it to Apple for notarisation and staples the ticket. Gatekeeper opens the application without a warning, and permissions survive updates.

### Secrets

Add these four secrets to your instance repository (**Settings > Secrets and variables > Actions**), or at the organisation level.

| Secret | Content |
| --- | --- |
| `MACOS_P12_BASE64` | Your "Developer ID Application" certificate with its private key, exported as `.p12`, base64-encoded |
| `MACOS_P12_PASSWORD` | Password chosen when exporting the `.p12` |
| `MACOS_CODESIGN_IDENTITY` | Name of the identity, for example `Developer ID Application: Example Org (ABCDE12345)` |
| `MACOS_NOTARIZE_JSON` | App Store Connect API key in the `rcodesign` JSON format, base64-encoded |

Signing is enabled as soon as `MACOS_P12_BASE64` exists. Provide all four secrets: with only some of them, the macOS jobs fail.

### Prepare the values

Export the certificate from Keychain Access as `developer-id.p12`, then:

```sh
base64 -i developer-id.p12 -o developer-id.p12.b64
security find-identity -v -p codesigning
```

The second command prints the identity name to use for `MACOS_CODESIGN_IDENTITY`.

Create an App Store Connect API key (App Store Connect > Users and Access > Integrations). Note the issuer ID and the key ID, and download the `.p8` file. Convert it with `rcodesign`:

```sh
rcodesign encode-app-store-connect-api-key -o notarize.json <issuer-id> <key-id> AuthKey_<key-id>.p8
base64 -i notarize.json -o notarize.json.b64
```

Store the secrets with the GitHub CLI, from your instance repository:

```sh
gh secret set MACOS_P12_BASE64 < developer-id.p12.b64
gh secret set MACOS_P12_PASSWORD
gh secret set MACOS_CODESIGN_IDENTITY --body "Developer ID Application: Example Org (ABCDE12345)"
gh secret set MACOS_NOTARIZE_JSON < notarize.json.b64
```

Delete the local `.p12`, `.b64` and `.json` files afterwards.

### Check

After a build, on a Mac:

```sh
spctl --assess --type open --context context:primary-signature -v remote-support-1.5.3-macos-aarch64.dmg
```

The answer must contain `accepted` and `Notarized Developer ID`.

### Notes

- The instance workflow must keep `secrets: inherit`. Without it the secrets do not reach the generator workflow.
- Keep the same Developer ID and the same `BUNDLE_ID` across releases. Changing either one makes macOS ask for the permissions again.
- The secrets are only used by the macOS jobs.
