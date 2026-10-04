# Gira Smart Home in a browser

The Windows (and macOS) client application for the Gira X1 smart home server
is an electron app that just bundles a webinterface. This code extracts the app
and can build a docker container for you, so that you can just host this
webinterface somewhere on your own infrastructure, so that you don't need a
Windows or macOS computer to access your X1 server.

Since nobody at Gira ever tested this thing on real browsers, things break a bit.
For this reason, there are a bunch of patches that remove restrictions like
right clicking, zooming etc. or fix broken rendering in other browsers like
Firefox. A few things are untested, expect brokenness. Also, the API server on
port :4432 uses a TLS cert that is not signed by any public CA, so you need to
visit this server once and whitelist its cert in your browser, otherwise
connections will fail. See [Connect to your X1](#connect-to-your-x1).

Requires Python 3.11+ and an installed `innoextract` on PATH. Run:

```sh
python3 setup.py
python3 server.py
```

Open **http://127.0.0.1:8080/**. Stop the server with Ctrl+C.

If no `.exe` is present beside `setup.py`, setup downloads
[Gira Smart Home 6.0.72](https://download.gira.de/data3/SmartHomeSetup_win32-x64-release-6.0.72.exe)
and keeps the installer there for subsequent runs. An existing installer is reused.
Interrupted downloads are discarded so the next run can retry.

For a newer installer, or when multiple installers are present:

```sh
python3 setup.py /path/to/SmartHomeSetup-new.exe
```

Setup uses the installed innoextract, extracts the installer temporarily, applies
all patches in `patches/series.json`, and publishes the static application in
`web/`. It never executes the Windows installer. Rerunning setup replaces the
previous generated `web/`; it does not accumulate extraction or backup folders.
A failed extraction or patch leaves the previous build intact.

Install innoextract with your system package manager before running setup.
To use an executable outside PATH, pass
`python3 setup.py --innoextract /path/to/innoextract` or set `INNOEXTRACT`.
Setup downloads only the app installer when needed; it never downloads
innoextract. No pip or npm packages are needed.

## Connect to your X1

Before connecting, add the X1 certificate exception in the **same browser/profile**:

1. Open `https://<x1-address>:4432/` (replace `<x1-address>` with your device’s IP or hostname).
2. Inspect the certificate warning, then choose **Advanced → Accept the Risk and Continue**
   in Firefox, or the equivalent proceed option in Chrome.
3. Return to the application and reload.

**Port 4432 matters.** Port 443 is the administration interface. An HTTP error
after accepting the exception is normal: port 4432 expects a WebSocket handshake.
If browser policy disallows exceptions, configure proper certificate trust.

Under **System → Verbindung zum Gira Gerät**, enter the X1 IP or hostname without
`https://`, and your app credentials. The browser connects directly to
`wss://<device>:4432/gds/api?...`; the web server only serves static assets.
Use the same account as Android to load the same per-user preferences, including
the temperature sensor selected for the status bar. Accounts without a user
profile can trigger the vendor's GDS 112 / `e.object is undefined` error when
reading temperature preferences; use the account configured in your working app.

Never share the WebSocket query string: it contains encoded credentials.
The vendor browser adapter saves credentials in localStorage; use a trusted,
dedicated origin rather than hosting unrelated scripts alongside this app.

## Docker with nginx

Build the browser assets once, then start the container:

```sh
python3 setup.py
docker compose up -d --build
```

Open **http://localhost:8080/**, or `http://<server-IP>:8080/` from your LAN.
The image contains the generated `web/` assets and uses the
[official nginx image](https://github.com/nginx/docker-nginx). Python and
innoextract are needed only to prepare the assets on the build machine.
Stop `server.py` first if it already occupies port 8080, or choose another port:

```sh
GIRA_PORT=8081 docker compose up -d --build
```

Set `GIRA_BIND=127.0.0.1` to restrict the published port to this computer;
by default it listens on all IPv4 interfaces. Keep any port/bind overrides in
your environment or a local `.env` file for subsequent Compose commands.

After changing the installer or patches, run `python3 setup.py` followed by
`docker compose up -d --build` again. Assets are copied into the image, so a
setup run alone does not update the running container. nginx asks browsers to
revalidate assets on reload because vendor filenames do not change between builds.

```sh
docker compose logs -f gira
docker compose down
```

The container serves HTTP assets; your browser still connects directly to the
X1 over WSS. The certificate exception on **port 4432** described above remains
necessary. Use your existing HTTPS reverse proxy if you need TLS for the web
page itself. Docker build context excludes the installer and project sources.

## GitLab container registry

The pipeline in `.gitlab-ci.yml` installs Python and innoextract, runs setup to
download/extract/patch the app, then builds and pushes the nginx image to this
project's registry (`CI_REGISTRY_IMAGE`). Branch and tag pipelines publish the
full commit SHA as the image tag; the default branch also publishes `latest`.
Both tags include `linux/amd64` and `linux/arm64/v8`; Docker selects the matching
architecture when pulling. The job uses a Buildx container builder and its
[bundled QEMU emulators](https://docs.docker.com/build/building/multi-platform/)
to validate nginx for both platforms. The extracted web assets are shared by both.

Enable the project's container registry and use a runner configured for
[Docker-in-Docker with TLS](https://docs.gitlab.com/ci/docker/docker_in_docker/#docker-in-docker-with-tls-enabled-in-the-docker-executor):
privileged Docker services with `/certs/client` shared between the job and service.
The job stores the daemon endpoint and client certificates in a named Docker
context so Buildx can connect with TLS, then selects its builder explicitly.
GitLab supplies `CI_REGISTRY`, `CI_REGISTRY_USER`, and `CI_REGISTRY_PASSWORD`
automatically; no personal registry credentials need to be added to the repository.
The runner needs outbound access to Gira downloads, Alpine packages, Docker Hub,
and the GitLab registry.

Find the image path under **Deploy → Container Registry** in GitLab. Use its
`:latest` tag for the default branch or `:<full-commit-SHA>` for a specific build.

## Serving with Python

The default server listens locally. For LAN access:

```sh
python3 server.py --bind 0.0.0.0
```

Use `--port 8081` if port 8080 is occupied. For permanent hosting, serve only
`web/` with your usual web server, with `index.html` as the directory index and
JavaScript MIME types for `.js`. Each browser needs network access to the X1.
Opening the files through `file://` will not work with the ES modules.

After rebuilding, hard-refresh with **Ctrl+Shift+R**. Stop the local server before
rerunning setup, then start it again after the build completes.

## Patches and compatibility

See [patches/README.md](patches/README.md). Every source fragment must match
exactly once; changed or ambiguous anchors stop setup for review rather than
silently applying a patch to a new release. `web/build-manifest.json` records
the installer hash, extractor version, patch hashes, and generated asset hashes.
Matching anchors alone do not prove a newer release works.

Version 6.0.72 was checked in Chrome and Firefox against a real X1: login, room
rendering, and live sensor reads worked. Firefox required the explicit content
height in patch 009; the doctype alone did not fix its blank room view. Detail
controls additionally need patches 010/011 for explicit nested heights, correct
SVG dial sizing, and the modern flex layout in Firefox. Demo dimmers, climate controls, settings, and timer
transitions were checked in both browsers, with dimmer geometry checked at four
window sizes. Device control writes were not tested.

Browser device discovery and native video/IP-link actions are stubs. S1 setup
references a missing development helper at localhost:8184. Camera, weather, door
communication, and mobile native features remain unverified. The original Gira
license notices are retained; these scripts do not grant redistribution rights.
