#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os

from .layout import KeyboardLayout
# layout = KeyboardLayout('../layouts/prog.toml')

def keyboard_server(file_path):

    host_name = 'localhost'
    server_port = 8080

    layout = KeyboardLayout(file_path)

    def main_page():
        return f"""
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta charset="utf-8" />
                <title>Kalamine</title>
                <link rel="stylesheet" type="text/css" href="style.css" />
                <script src="x-keyboard.js" type="module"></script>
                <script src="demo.js" type="text/javascript"></script>
            </head>
            <body>
                <p>
                    <a href="{layout.meta['url']}">{layout.meta['name']}</a>
                    <br />
                    {layout.meta['description']}
                </p>
                <input spellcheck="false" placeholder="" />
                <x-keyboard src="/json"></x-keyboard>
                <p style="text-align: right;">
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
                    | <a href="/xkb">xkb</a>
                    | <a href="/xkb_custom">xkb_custom</a>
                </p>
            </body>
            </html>
        """

    class LayoutHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            www_path = os.path.join(dir_path, 'www')
            super().__init__(*args, directory=www_path, **kwargs)

        def do_GET(self):
            self.send_response(200)

            def send(page, content='text/plain', charset='utf-8'):
                self.send_header('Content-type', f"{content}; charset={charset}")
                self.end_headers()
                self.wfile.write(bytes(page, charset))
                # self.wfile.write(page.encode(charset))

            if self.path == '/json':
                send(json.dumps(layout.json), content='application/json')
            elif self.path == '/keylayout':
                # send(layout.keylayout, content='application/xml')
                send(layout.keylayout)
            elif self.path == '/klc':
                send(layout.klc, charset='utf-16-le')
            elif self.path == '/xkb':
                send(layout.xkb)
            elif self.path == '/xkb_custom':
                send(layout.xkb_patch)
            elif self.path == '/':
                # send(main_page(), content='application/xhtml+xml')
                send(main_page(), content='text/html')
            else:
                return SimpleHTTPRequestHandler.do_GET(self)

    webServer = HTTPServer((host_name, server_port), LayoutHandler)
    print(f"Server started: http://{host_name}:{server_port}")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Server stopped.')
