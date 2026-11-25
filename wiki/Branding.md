[[Français|Branding-fr]]

# Branding

The visual identity of a client comes from three places:

| What | Where |
| --- | --- |
| Application name | `APP_NAME` in `client.env` |
| Accent colour | `ACCENT_COLOR` in `client.env` |
| Icons and logos | PNG files in the `branding/` directory of the instance |

Anything else in the interface is changed with patches. See [[Custom UI patches|Custom-UI-Patches]].

## Files

```text
branding/
  icon.png                 required
  logo.png                 optional
  logo_light.png           optional
  logo_dark.png            optional
  mac-tray-dark-x2.png     optional
  mac-tray-light-x2.png    optional
```

| File | Required | Rules | Use |
| --- | --- | --- | --- |
| `icon.png` | yes | Square PNG, at least 256x256. 1024x1024 recommended. | Source of every application icon. |
| `logo.png` | no | Copied as is. | Replaces the RustDesk asset `flutter/assets/logo.png`. |
| `logo_light.png` | no | Copied as is. | Replaces `flutter/assets/logo_light.png`. |
| `logo_dark.png` | no | Copied as is. | Replaces `flutter/assets/logo_dark.png`. |
| `mac-tray-dark-x2.png` | no | Copied as is. | Replaces the macOS menu bar icon `res/mac-tray-dark-x2.png`. |
| `mac-tray-light-x2.png` | no | Copied as is. | Replaces the macOS menu bar icon `res/mac-tray-light-x2.png`. |

Other files in `branding/` are ignored.

## icon.png

The build stops when `icon.png` is missing, is not square, or is smaller than 256x256.

Every icon shipped by RustDesk is generated from this single file:

| Generated file | Content |
| --- | --- |
| `res/icon.ico`, `flutter/windows/runner/resources/app_icon.ico` | Windows icon with sizes 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256 |
| `res/tray-icon.ico` | Windows tray icon with sizes 16, 24, 32 and 48 |
| `res/icon.png`, `res/mac-icon.png` | 1024x1024 |
| `res/32x32.png`, `res/64x64.png`, `res/128x128.png`, `res/128x128@2x.png` | Linux and packaging icons |
| `res/scalable.svg`, `flutter/assets/icon.svg` | The 256x256 PNG wrapped in an SVG file |
| `flutter/assets/icon.png` | 256x256 |
| `flutter/macos/Runner/AppIcon.icns` and the `AppIcon.appiconset` images | macOS application icon |

Advice:

- Provide 1024x1024. A smaller icon is enlarged for the large sizes and looks soft.
- Keep the design readable at 16x16: it is also the tray icon.
- Use a transparent background if the icon is not a full square. Transparency is kept.
- The SVG files only wrap a bitmap. A vector source brings no benefit: export it to PNG.

## Optional files

The optional files are copied without any conversion or check. Each one replaces the upstream file of the same name. Open that file in the RustDesk sources at the version you build, and use the same dimensions and the same kind of background.

When an optional file is absent, the upstream image stays in the client. Check the screens of your client and add the logo files if the RustDesk logo is still visible somewhere.

## Not customisable yet

- The privacy-screen image, shown on the remote display while privacy mode is active.
- The Linux package name and binary name, which stay `rustdesk`.

## Do not reuse the RustDesk logo

"RustDesk" and its logo belong to their owner. Use your own name and your own artwork. `APP_NAME` cannot be `RustDesk`.
