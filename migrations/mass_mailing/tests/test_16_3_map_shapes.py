# -*- coding: utf-8 -*-
from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("saas~16.3")
class TestMapShapes(UpgradeCase):
    def prepare(self):
        arch = """
<div class="some_arch_nesting">
    <div class="container">
        <div class="row">
            <div class="col-lg-4">
                <div class="card">
                    <img class="card-img-top"
                        src="/web/image/353-97f62ac9/s_default_image_three_cols_1.svg"
                        data-original-id="220"
                        data-original-src="/mass_mailing/static/src/img/theme_default/s_default_image_three_cols_1.jpg"
                        data-mimetype="image/svg+xml"
                        data-shape="mass_mailing/basic/circle"
                        data-file-name="s_default_image_three_cols_1.svg"
                        data-shape-colors=";;;;"
                        data-original-mimetype="image/jpeg">
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card">
                    <img class="card-img-top"
                        src="/web/image/352-bd909c0a/s_default_image_three_cols_2.svg"
                        data-original-id="221"
                        data-original-src="/mass_mailing/static/src/img/theme_default/s_default_image_three_cols_2.jpg"
                        data-mimetype="image/svg+xml"
                        data-shape="mass_mailing/basic/triangle"
                        data-file-name="s_default_image_three_cols_2.svg"
                        data-shape-colors=";;;;"
                        data-original-mimetype="image/jpeg">
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card">
                    <img class="card-img-top"
                        src="/web/image/354-bda997e6/s_default_image_three_cols_3.svg"
                        data-original-id="222"
                        data-original-src="/mass_mailing/static/src/img/theme_default/s_default_image_three_cols_3.jpg"
                        data-mimetype="image/svg+xml"
                        data-shape="mass_mailing/basic/slanted"
                        data-file-name="s_default_image_three_cols_3.svg"
                        data-shape-colors=";;;;"
                        data-original-mimetype="image/jpeg">
                </div>
            </div>
        </div>
    </div>
</div>
        """.replace("\\\n", "")
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Map Shapes Test",
                "body_arch": arch,
                "body_html": '<div class="some_html_nesting">%s</div>' % arch,
            }
        )
        return {"mailing_id": mailing.id}

    def check(self, init):
        mailing = self.env["mailing.mailing"].browse(init["mailing_id"])
        for field in ["body_arch", "body_html"]:
            body = mailing[field]
            root_el = html.fromstring(f"<wrap>{body}</wrap>", parser=utf8_parser)
            image_els = root_el.xpath("//img")
            # Image 0
            self.assertEqual(
                image_els[0].get("src"),
                "/web/image/353-97f62ac9/s_default_image_three_cols_1.svg",
                "Image source should not have been changed",
            )
            self.assertEqual(
                image_els[0].get("data-shape"),
                "web_editor/geometric_round/geo_round_circle",
                "Image shape should have been mapped",
            )
            # Image 1
            self.assertEqual(
                image_els[1].get("src"),
                "/web/image/352-bd909c0a/s_default_image_three_cols_2.svg",
                "Image source should not have been changed",
            )
            self.assertEqual(
                image_els[1].get("data-shape"),
                "web_editor/geometric/geo_cornered_triangle",
                "Image shape should have been mapped",
            )
            # Image 2
            self.assertEqual(
                image_els[2].get("src"),
                "/web/image/354-bda997e6/s_default_image_three_cols_3.svg",
                "Image source should not have been changed",
            )
            self.assertEqual(
                image_els[2].get("data-shape"),
                "web_editor/geometric/geo_slanted",
                "Image shape should have been mapped",
            )
