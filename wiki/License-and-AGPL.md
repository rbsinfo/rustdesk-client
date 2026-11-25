[[Français|License-and-AGPL-fr]]

# License and AGPL

This page is a practical summary. It is not legal advice. The text of the licence is the reference: see the `LICENSE` file of the generator and of RustDesk.

## Who owns what

| Item | Licence | Owner |
| --- | --- | --- |
| RustDesk | AGPL-3.0 | Its authors. "RustDesk" is a trademark of its owner. |
| `rustdesk-client` (this generator) | AGPL-3.0 | Its contributors |
| Your instance repository | Your configuration, icons and patches | You |
| The client you build | AGPL-3.0, as a modified version of RustDesk | RustDesk authors for the original code, you for your changes |

`rustdesk-client` is an independent project. It is not affiliated with, endorsed by or supported by RustDesk or Purslane. The clients you build are not official RustDesk products.

## What the AGPL asks of you

You distribute a client as soon as someone outside your organisation receives it: a customer, a partner, a user who downloads it from your site.

When you distribute a client, you must:

1. **Offer the complete corresponding source** to everyone who receives the client. That is the RustDesk sources as modified for your build, your patches included.
2. **Keep the notices**: copyright notices, licence text, and the statement that the program is under the AGPL-3.0.
3. **State that the program was modified.**
4. **Pass on the same rights.** Recipients may use, study, modify and redistribute the client under the AGPL-3.0. You cannot add restrictions.

## What the generator does for you

| Obligation | How it is covered |
| --- | --- |
| Complete corresponding source | Every build archives the RustDesk sources after `apply.py` and your patches have been applied. Every release attaches it as `<slug>-<version>-source.tar.gz`. |
| Notices | The upstream copyright notice and licence are kept in the sources and on the About page. |
| Statement of modification | The About page shows `Built by <COMPANY>. Modified version of RustDesk (AGPL-3.0).` |
| Where to find the source | The About page shows `Source code: <SOURCE_URL>` when `SOURCE_URL` is set. |
| Release text | The release description states that the client is a modified version of RustDesk under the AGPL-3.0, and that the source is attached. |

## What remains your job

- **Set `SOURCE_URL`** in `client.env`. Point it to a place where recipients can get the source: your instance repository if it is public, or a page that offers the archive.
- **Make the source reachable.** If your instance repository is private, its releases are private too. Publish the `-source.tar.gz` of each version you distribute somewhere your users can reach, at no charge.
- **Keep the source of each version you distributed**, not only the latest.
- **Distribute the matching archive.** The source archive of a release corresponds to the binaries of the same release.
- **Do not remove the notices** with a patch. Do not present the client as official RustDesk software.

```ini
SOURCE_URL=https://github.com/example-org/remote-support
```

## Trademark

"RustDesk" is a trademark of its owner. The AGPL gives you rights on the code, not on the name or the logo.

- `APP_NAME` cannot be `RustDesk`. The build refuses it.
- Use your own icon and logos. See [[Branding|Branding]].
- You may state the fact that your client is based on RustDesk. The About page does it.

## Questions

**Is my configuration secret?** No. The server host, the public key and every setting can be read from the client. A private instance repository hides nothing that the binary does not already reveal.

**Do I have to publish my instance repository?** No. You have to offer the corresponding source of what you distribute. The source archive covers it. A public instance repository is the simplest way to do so.

**We only use the client inside our organisation.** Internal use is generally not treated as distribution, but the boundary depends on your situation: contractors, subsidiaries, customers. Ask your legal counsel. Publishing the source archive removes the question.

**May I charge for the client or for support?** The AGPL does not forbid it. It forbids restricting the rights of recipients.
