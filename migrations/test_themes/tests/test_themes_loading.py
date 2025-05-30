import requests

from odoo.tools import config

try:
    from odoo.addons.http_routing.tests.common import MockRequest
except ImportError:
    from odoo.addons.website.tools import MockRequest

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

BASE_URL = "http://127.0.0.1:{}".format(config["http_port"])


@change_version("saas~13.5")
class TestThemesLoading(UpgradeCase):
    def prepare(self):
        """Creates 2 websites with Artists and Zap installed."""
        res = {}
        themes = self.env["ir.module.module"].search([("name", "in", ("theme_avantgarde", "theme_zap"))])
        for theme in themes:
            website = self.env["website"].create(
                {
                    "name": theme.name,
                    "theme_id": theme.id,
                }
            )
            theme._theme_get_stream_themes()._theme_load(website)
            res[theme.name] = website.id
        return res

    def check(self, init):
        Website = self.env["website"]
        # 1. Ensure old theme dependencies are removed
        website_zap = Website.browse(init["theme_zap"])
        views = self.env["ir.ui.view"].search(
            [
                ("key", "like", "treehouse"),
                ("website_id", "=", website_zap.id),
            ]
        )
        self.assertFalse(
            bool(views), "The views from treehouse should've been removed as Zap doesn't depend from Treehouse anymore."
        )

        # 2. Ensure the page can be rendered (some views from avantgarde & common should've been removed)
        session = requests.Session()
        for website in Website.browse(init.values()):
            # 2.1 Public rendering
            res = session.get("{}/?fw={}&debug=assets".format(BASE_URL, website.id))
            self.assertEqual(res.status_code, 200, "Ensure rendering went fine as public user")
            self.assertTrue(
                "/{}/static/src".format(website.theme_id.name) in res.text, "Ensure correct website was loaded"
            )
            self.assertTrue("error" not in res.text, "Ensure there is no error (css compilation or xpath)")

            with MockRequest(self.env, website=website):
                # 2.2 Test edit mode rendering
                # Ensure there is no xpath error, it should not crash (eg 'theme_common.s_animated_boxes_options')
                self.env["ir.ui.view"].with_context(website_id=website.id).render_public_asset("website.snippets")
