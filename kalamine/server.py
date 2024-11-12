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
            layout_name_displayed = (
                f"""<a href="{layout.meta['url']}">{layout.meta['name']} 🔗</a>"""
            )

        return f"""
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta charset="utf-8" />
                <title>Kalamine</title>
                <link rel="stylesheet" type="text/css" href="style.css" />
                <link rel="stylesheet" type="text/css" href="heatmap.css" />
                <script src="x-keyboard.js" type="module"></script>
                <script src="http://{host_name}:{lr_server_port}/livereload.js"></script>
                <script src="demo.js" type="text/javascript"></script>
                <script src="collapsable-table.js" type="module"></script>
                <script src="stats-canvas.js" type="module"></script>
                <script src="layout-analyzer.js" type="text/javascript"></script>
                <script src="keebs.js" type="text/javascript"></script>
                <script>angle_mod = {"true" if angle_mod else "false"}; </script>
            </head>
            <body>
                <h1>Kalamine</h1>
                <table class="table-fill">
	                <caption>{layout_name_displayed}</caption>
                    <tbody class="table-hover">
                        <tr>
                            <td class="col-left">Locale</td>
                            <td class="col-right">{layout.meta['locale']}/{layout.meta['variant']}</td>
                        </tr>
                        <tr>
                            <td class="col-left">Description</td>
                            <td class="col-right">{layout.meta['description']}</td>
                        </tr>
                        <tr>
                            <td class="col-left">Version</td>
                            <td class="col-right">{layout.meta['version']}</td>
                        </tr>
                    </tbody>
                </table>
                <input spellcheck="false" placeholder="zone de saisie {layout.meta['name']}" />
                <x-keyboard src="/json"></x-keyboard>
                <p style="text-align: center;" {"hidden" if angle_mod else ""}>
                    <select id="geometry">
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

                <h1>Analyseur</h1>
                <p id="imprecise-data">
                    <strong>Attention :</strong> cette disposition
                    ne supporte pas de nombreux caractères du corpus sélectionné.
                    Les résultats ne sont proposés qu’à titre indicatif.
                </p>
                <div id="sticky-select" style="text-align: center;">
                    <form>
                        <select id="layout" style="display:none"> <option value="{layout.meta["variant"]}" selected>{layout.meta["name"]}</option></select>
                        <select id="corpus" style="font-size: 1.2rem;text-align:center;">
                            <option>en</option>
                            <option selected>en+fr</option>
                            <option>fr</option>
                        </select>
                    </form>
                </div>
                <h2>Métriques</h2>
                <section id="load">
                    <h3>Charge des doigts</h3>
                    <small></small>
                    <stats-canvas></stats-canvas>
                </section>

                <section id="sfu">
                    <h3>Digrammes de même doigt/touche</h3>
                    <small><span id="sfu-all"></span> / <span id="sku-all"></span></small>
                    <stats-canvas></stats-canvas>
                </section>

                <collapsable-table id="Achoppements">
                <small>
                    <span id="unsupported-all"></span> /
                    <span id="sfu-all"></span> /
                    <span id="extensions-all"></span> /
                    <span id="scisors-all"></span>
                </small>
                <table id="unsupported"></table>
                <table id="sfu-digrams"></table>
                <table id="extended-rolls"></table>
                <table id="scisors"></table>
                </collapsable-table>

                <collapsable-table id="Digrammes">
                <small>
                    <span id="sku-all"></span> /
                    <span id="inward-all"></span> /
                    <span id="outward-all"></span>
                </small>
                <table id="sku-digrams"></table>
                <table id="inward"></table>
                <table id="outward"></table>
                </collapsable-table>

                <collapsable-table id="Trigrammes">
                <small>
                    <span id="almost-skb-all"></span> /
                    <span id="almost-sfb-all"></span> /
                    <span id="redirect-all"></span> /
                    <span id="bad-redirect-all"></span>
                </small>
                <table id="almost-skbs"></table>
                <table id="almost-sfbs"></table>
                <table id="redirect"></table>
                <table id="bad-redirect"></table>
                </collapsable-table>


                <h2>Glossaire</h2>
                <p>»»» <a href="https://ergol.org/ressources/glossaire">Un glossaire est en cours d’élaboration ici.</a> «««</p>

                <h2>Mise en garde</h2>
                <p><strong>Ces métriques ne sont pas des cibles d’optimisation !</strong></p>

                <blockquote cite="https://fr.wikipedia.org/wiki/Loi_de_Goodhart">
                <p>Lorsqu’une métrique devient un objectif, elle cesse d’être une bonne métrique.</p>
                <p style="text-align: right;">— <a
                    href="https://fr.wikipedia.org/wiki/Loi_de_Goodhart">loi de Goodhart</a></p>
                </blockquote>
                <blockquote>
                    <p>Les chiffres sont aux analystes ce que les lampadaires sont aux ivrognes :
                    ils fournissent bien plus un appui qu’un éclairage.
                    <p style="text-align: right;">— Jean Dion</p>
                    <!-- Le Devoir - 4 juin 1997 -->
                </blockquote>

                <p> Notre recommandation : utilisez ces métriques non pour mesurer les qualités
                d’une disposition de clavier, mais pour essayer d’en évaluer le défaut le plus
                gênant. Puis itérez sur votre layout jusqu’à ce que ce défaut soit
                suffisamment réduit… sans en créer un pire ailleurs. </p>

                <p> Et recommencez. :-) </p>
                <br>
                <p style="text-align:center;"> Fait avec ♥ grâce à <a href="https://github.com/OneDeadKey/kalamine">kalamine</a> v{metadata.version('kalamine')}</p>
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
        url = f"http://{host_name}:{webserver_port}/#/{kb_layout.meta['variant']}/ol60/en+fr"
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
