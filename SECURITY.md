# Security policy

## Reporting a vulnerability

Please use GitHub's private reporting: **Security > Report a vulnerability** on
<https://github.com/rbsinfo/rustdesk-client>. Do not open a public issue.

In scope: the scripts, patches and workflows of this repository, for example a
way to make a build embed settings other than those of its instance.

Vulnerabilities in RustDesk itself must be reported to the
[RustDesk project](https://github.com/rustdesk/rustdesk/security).

## What a client contains

Everything in `client.env` and `custom.json` is compiled into the client and
can be read by anyone who has it. The server public key is meant to be public.
Never put a password or a private key in an instance; `scripts/apply.py`
refuses `password` and `salt` for that reason.
