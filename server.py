#!/usr/bin/env python3
"""Serve the extracted Gira web app using only Python's standard library."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class AppHandler(SimpleHTTPRequestHandler):
    # The vendor bundle uses ES modules, which require a JavaScript MIME type.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="127.0.0.1", help="Use 0.0.0.0 to allow LAN access")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--directory", type=Path,
                        default=Path(__file__).resolve().parent / "web")
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not all((directory / name).is_file() for name in ("index.html", "layout.html")):
        parser.error(f"{directory} is not a built app; run python3 setup.py first")
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")

    # Serve only the web assets, independently of the caller's working directory.
    handler = partial(AppHandler, directory=str(directory))
    try:
        server = ThreadingHTTPServer((args.bind, args.port), handler)
    except OSError as error:
        parser.exit(1, f"Cannot start server: {error}. Try --port 8081.\n")
    with server:
        host = "127.0.0.1" if args.bind == "0.0.0.0" else args.bind
        port = server.server_port
        print(f"Gira Smart Home: http://{host}:{port}/", flush=True)
        if args.bind == "0.0.0.0":
            print(f"LAN access: http://<this-computer-IP>:{port}/", flush=True)
        print("Press Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
