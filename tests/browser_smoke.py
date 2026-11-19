"""Exercise the published app at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.wait_for_selector('#cards article')
                page.fill('#q','Wheat Board')
                assert page.locator('#cards article').count()==1
                page.locator('#cards summary').click()
                assert page.locator('#cards ul a').count()>0
                assert 'cwb.ca' in page.locator('#cards').inner_text()
                page.select_option('#group','Commission records')
                assert 'No resources' in page.locator('#cards').inner_text()
                page.select_option('#group','')
                with page.expect_download() as dl:page.click('#csv')
                assert dl.value.suggested_filename.endswith('.csv')
                page.screenshot(path=str(screenshots/'desktop.png'))
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                page.screenshot(path=str(screenshots/'mobile.png'))
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, filters, source evidence, export and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
