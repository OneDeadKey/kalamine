import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
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
        return f"""
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta charset="utf-8" />
                <title>Kalamine</title>
                <link rel="stylesheet" type="text/css" href="style.css" />
                <script src="x-keyboard.js" type="module"></script>
                <script src="http://{host_name}:{lr_server_port}/livereload.js"></script>
                <script src="demo.js" type="text/javascript"></script>
                <script>angle_mod = {"true" if angle_mod else "false"}; </script>
            </head>
            <body>
                <p>
                    <a href="{layout.meta['url']}">{layout.meta['name']}</a>
                    <br /> {layout.meta['locale']}/{layout.meta['variant']}
                    <br /> {layout.meta['description']}
                </p>
                <input spellcheck="false" placeholder="" />
                <x-keyboard src="/json"></x-keyboard>
                <p style="text-align: right;" {"hidden" if angle_mod else ""}>
                    <select>
                        <option value="iso">  ISO  </option>
                        <option value="ansi"> ANSI </option>
                        <option value="ol60"> ERGO </option>
                        <option value="ol50"> 4×12 </option>
                        <option value="ol40"> 3×12 </option>
                    </select>
                </p>
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
            </body>
            </html>
        """

    class LayoutHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore
            kwargs["directory"] = str(Path(__file__).parent / "www")
            super().__init__(*args, **kwargs)

        def do_GET(self) -> None:
            self.send_response(200)

            def send(
                page: str, content: str = "text/plain", charset: str = "utf-8"
            ) -> None:
                self.send_header("Content-type", f"{content}; charset={charset}")
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
