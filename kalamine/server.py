import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from importlib import metadata
from pathlib import Path
from xml.etree import ElementTree as ET

import click
from livereload import Server  # type: ignore

from .generators import ahk, keylayout, klc, web, xkb
from .layout import KeyboardLayout, load_layout


def keyboard_server(file_path: Path, angle_mod: bool = False) -> None:
    kb_layout = KeyboardLayout(load_layout(file_path), angle_mod)

    host_name = "localhost"
    webserver_port = 1664
    lr_server_port = 5500

    def main_page(layout: KeyboardLayout, angle_mod: bool = False) -> str:
        layout_ref = layout.meta["name"]
        if "url" in layout.meta:
            layout_ref = f"""<a href="{layout.meta['url']}">{layout.meta['name']}</a>"""

        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Kalamine</title>
                <link rel="stylesheet" type="text/css" href="style.css">
                <script src="http://{host_name}:{lr_server_port}/livereload.js"></script>
                <script type="module" src="mjs/x-keyboard.js"></script>
                <script type="module" src="mjs/layout-analyzer.js"></script>
                <script type="module" src="mjs/stats-canvas.js"></script>
                <script type="module" src="mjs/stats-table.js"></script>
                <script type="module" src="mjs/stats.js"></script>
                <script type="text/javascript" src="demo.js"></script>
                <script>angle_mod = {"true" if angle_mod else "false"}; </script>
            </head>
            <body>
                <p style="float: right; text-align: right;">
                    <a href="https://github.com/OneDeadKey/kalamine">kalamine</a>
                    v{metadata.version('kalamine')}<br>🦆
                </p>
                <dl>
                    <dt>Name</dt>
                    <dd>{layout_ref}</dd>
                    <dt>Locale</dt>
                    <dd>{layout.meta['locale']}/{layout.meta['variant']}</dd>
                    <dt>Description</dt>
                    <dd>{layout.meta['description']}</dd>
                    <dt>Version</dt>
                    <dd>{layout.meta['version']}</dd>
                </dl>
                <input spellcheck="false" placeholder="{layout.meta['name']}">
                <x-keyboard src="/json"></x-keyboard>
                <p style="text-align: center;">
                    <a href="/json">json</a>
                    | <a href="/keylayout">keylayout</a>
                    | <a href="/klc">klc</a>
                    | <a href="/rc">rc</a>
                    | <a href="/c">c</a>
                    | <a href="/xkb_keymap">xkb_keymap</a>
                    | <a href="/xkb_symbols">xkb_symbols</a>
                    | <a href="/svg">svg</a>
                </p>
                <div id="sticky-select">
                    <form>
                        <label for="geometry">geometry</label>
                        <select id="geometry" {"hidden" if angle_mod else ""}>
                            <option value="iso">  ISO  </option>
                            <option value="ansi"> ANSI </option>
                            <option value="ol60"> ERGO </option>
                            <option value="ol50"> 4×6  </option>
                            <option value="ol40"> 3×6  </option>
                        </select>
                        <select id="corpus">
                            <option selected>-</option>
                            <option>en</option>
                            <option>en+fr</option>
                            <option>fr</option>
                        </select>
                        <label for="corpus">corpus</label>
                    </form>
                    <p id="imprecise-data" hidden>
                        <strong>Warning:</strong> many characters in the selected corpus
                        are not supported by this layout. Results cannot be trusted.
                    </p>
                </div>
                <div id="analyzer" hidden>
                    <section id="load">
                        <h2>Finger Load</h2>
                        <small></small>
                        <stats-canvas></stats-canvas>
                    </section>
                    <section id="sfu">
                        <h2>Same Finger/Key Usage</h2>
                        <small>
                            SFU: <span id="sfu-total"></span> /
                            SKU: <span id="sku-total"></span>
                        </small>
                        <stats-canvas></stats-canvas>
                    </section>
                    <section id="bottlenecks">
                        <h2>Bottlenecks</h2>
                        <small>total:
                            <span id="unsupported-all"></span> /
                            <span id="sfu-all"></span> /
                            <span id="extensions-all"></span> /
                            <span id="scissors-all"></span>
                        </small>
                        <stats-table>
                            <table id="unsupported"    title="unsupported"></table>
                            <table id="sfu-bigrams"    title="SFU"></table>
                            <table id="extended-rolls" title="LFB"></table>
                            <table id="scissors"       title="scissors"></table>
                        </stats-table>
                    </section>
                    <section id="bigrams">
                        <h2>Bigrams</h2>
                        <small>total:
                            <span id="sku-all"></span> /
                            <span id="inward-all"></span> /
                            <span id="outward-all"></span>
                        </small>
                        <stats-table>
                            <table id="sku-bigrams" title="SKU"></table>
                            <table id="inward"      title="inward rolls"></table>
                            <table id="outward"     title="outward rolls"></table>
                        </stats-table>
                    </section>
                    <section id="trigrams">
                        <h2>Trigrams</h2>
                        <small>total:
                            <span id="sks-all"></span> /
                            <span id="sfs-all"></span> /
                            <span id="redirect-all"></span> /
                            <span id="bad-redirect-all"></span>
                        </small>
                        <stats-table>
                            <table id="sks"          title="SKS"></table>
                            <table id="sfs"          title="SFS"></table>
                            <table id="redirect"     title="redirects"></table>
                            <table id="bad-redirect" title="bad redirects"></table>
                        </stats-table>
                    </section>
                </div>
            </body>
            </html>
        """

    class LayoutHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore
            kwargs["directory"] = str(Path(__file__).parent / "www")
            super().__init__(*args, **kwargs)
            self.extensions_map = {
                "json": "application/json",
                "css": "text/css",
                "js": "text/javascript",
            }

        def do_GET(self) -> None:
            self.send_response(200)

            def send(
                page: str, content: str = "text/plain", charset: str = "utf-8"
            ) -> None:
                self.send_header("Content-type", f"{content}; charset={charset}")
                # no cash as one is likely working live on it
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                self.wfile.write(bytes(page, charset))
                # self.wfile.write(page.encode(charset))

            # XXX always reloads the layout on the root page, never in sub pages
            nonlocal kb_layout
            nonlocal angle_mod
            if self.path == "/favicon.ico":
                pass
            elif self.path == "/json":
                send(web.pretty_json(kb_layout), content="application/json")
            elif self.path == "/keylayout":
                # send(keylayout.keylayout(kb_layout), content='application/xml')
                send(keylayout.keylayout(kb_layout))
            elif self.path == "/ahk":
                send(ahk.ahk(kb_layout))
            elif self.path == "/klc":
                send(klc.klc(kb_layout), charset="utf-16-le", content="text")
            elif self.path == "/rc":
                send(klc.klc_rc(kb_layout), content="text")
            elif self.path == "/c":
                send(klc.klc_c(kb_layout), content="text")
            elif self.path == "/xkb_keymap":
                send(xkb.xkb_keymap(kb_layout))
            elif self.path == "/xkb_symbols":
                send(xkb.xkb_symbols(kb_layout))
            elif self.path == "/svg":
                utf8 = ET.tostring(web.svg(kb_layout).getroot(), encoding="unicode")
                send(utf8, content="image/svg+xml")
            elif self.path == "/":
                kb_layout = KeyboardLayout(load_layout(file_path), angle_mod)  # refresh
                send(main_page(kb_layout, angle_mod), content="text/html")
            else:
                return SimpleHTTPRequestHandler.do_GET(self)

    webserver = HTTPServer((host_name, webserver_port), LayoutHandler)
    thread = threading.Thread(None, webserver.serve_forever)

    try:
        thread.start()
        url = f"http://{host_name}:{webserver_port}"
        print(f"Server started: {url}")
        print("Hit Ctrl-C to stop.")
        webbrowser.open(url)

        # livereload
        lr_server = Server()
        lr_server.watch(str(file_path))
        lr_server.serve(host=host_name, port=lr_server_port)

    except KeyboardInterrupt:
        pass

    webserver.shutdown()
    webserver.server_close()
    thread.join()
    click.echo("Server stopped.")
