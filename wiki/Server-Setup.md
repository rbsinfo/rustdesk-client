[[Français|Server-Setup-fr]]

# Server setup

This page lists what the client needs from your server. It does not replace the installation guide of the server you choose.

## What the client needs

| Need | Where it goes |
| --- | --- |
| Host name of the ID server (`hbbs`) | `SERVER_HOST` in `client.env` |
| Public key of the server (`id_ed25519.pub`) | `SERVER_KEY` in `client.env` |
| A relay server (`hbbr`) reachable by the clients | Nothing to configure in the instance. Run `hbbr` on the same host, or declare the relay on `hbbs`. |
| Optional: URL of an API server or web console | `API_URL` in `client.env` |

These values are compiled into the client and cannot be changed by the user. Changing the host or the key later means building and distributing a new client.

Use a DNS name rather than an IP address for `SERVER_HOST`. You can then move the server without rebuilding.

## Ports

Open these ports from the clients to the server:

| Port | Protocol | Service | Use |
| --- | --- | --- | --- |
| 21115 | TCP | `hbbs` | NAT type test |
| 21116 | TCP and UDP | `hbbs` | ID registration, heartbeat, connection setup |
| 21117 | TCP | `hbbr` | Relay |

If `hbbs` listens on another port than 21116, add it to the host:

```ini
SERVER_HOST=rustdesk.example.com:31116
```

The API server or console has its own address and port. Put the full URL in `API_URL`.

## Public key

`hbbs` creates a key pair on its first start, in its working directory:

| File | Keep it |
| --- | --- |
| `id_ed25519` | Private. It stays on the server. Never put it in a repository. |
| `id_ed25519.pub` | Public. Its content is the value of `SERVER_KEY`. |

```sh
cat id_ed25519.pub
```

The value is 44 base64 characters ending with `=`.

Back up both files. If the server loses its key pair, every client you distributed refuses the new key, and you must rebuild and redistribute.

## RustDesk Server OSS or a console

| Server | What you get | `API_URL` |
| --- | --- | --- |
| RustDesk Server OSS (`hbbs` + `hbbr`) | Remote sessions through your own server. No device list. | Leave empty |
| RustDesk Server Pro, or a compatible console such as CortenDesk | The same, plus a web console that lists the devices | URL of the console API |

With `API_URL` set, the client reports to the console: it posts to `/api/sysinfo` and `/api/heartbeat`. The device appears with:

- its ID,
- its host name,
- the user name,
- the operating system,
- the client version.

The client does not send the application name. If several clients built from different instances report to the same console, the console cannot tell them apart by name. Group the devices on the server side.

## The technician side

The template builds an incoming-only client: it is the one installed on the machines you support. To take control, the technician uses a client that can make outgoing connections and that is configured with the same server and key. That can be:

- a standard RustDesk client, configured by hand with your server and key, or
- a second instance without `"conn-type": "incoming"` in `custom.json`.

## Checklist

1. `hbbs` and `hbbr` are running, and ports 21115 to 21117 are reachable from outside.
2. `SERVER_HOST` resolves from the networks of your users.
3. `SERVER_KEY` is the exact content of `id_ed25519.pub`.
4. If you use a console, `API_URL` opens from a browser on a user machine.
5. A test client shows a ready status and can be reached by its ID.
