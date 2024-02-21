# -*- coding: utf-8 -*-

import re

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("saas~17.2")
class TestMobileOrders(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Mobile Orders Test" t-name="website.mobile_orders_test">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'mobile orders test'"/>
        <div id="wrap" class="oe_structure oe_empty">
            <section class="s_three_columns pt32 pb32" data-snippet="s_three_columns" data-name="Columns">
                <div class="container">
                    <div class="row d-flex">
                        <div id="col1-with-changes" class="col-6 order-lg-0 order-1" style="--order: 3;">
                            <p>Order class (order-1) removed and inline order style after fix. Keep inline CSS variable.</p>
                        </div>
                        <div id="col2-with-changes" class="col-6 order-lg-0 order-0 custom-order-2 order-4-custom">
                            <p>Order class (order-0) removed and inline order style after fix. Keep custom classes.</p>
                        </div>
                    </div>
                </div>
            </section>
            <section class="s_three_columns pt32 pb32" data-snippet="s_three_columns" data-name="Columns">
                <div class="container">
                    <div class="row d-flex">
                        <div id="col3-no-change" class="col-6 order-lg-0" style="--order: 3; order: 1;">
                            <p>No change after fix.</p>
                        </div>
                        <div id="col4-no-change" class="col-6 order-lg-0 custom-order-2 order-4-custom" style="order: 0;">
                            <p>No change after fix.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>
        """
        view = self.env["ir.ui.view"].create(
            {
                "name": "Mobile Orders Test",
                "type": "qweb",
                "key": "website.mobile_orders_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace(r"\n", ""),
            }
        )
        return {"view_id": view.id}

    def check(self, init):
        arch = self.env["ir.ui.view"].browse(init["view_id"]).arch_db
        root_el = html.fromstring(f"<wrap>{arch}</wrap>", parser=utf8_parser)

        def get_classes_styles(col_id):
            col = root_el.find(f".//div[@id='{col_id}']")
            return [re.split(r"\s+", col.get("class")), re.split(r"(?<=;)\s+", col.get("style"))]

        for classes, styles in [get_classes_styles("col1-with-changes"), get_classes_styles("col3-no-change")]:
            self.assertNotIn("order-1", classes, "Should not have a mobile order class")
            self.assertIn("order-lg-0", classes, "Should have an order-lg-0 class for desktops")
            self.assertIn("order: 1;", styles, "Should have an inline style order: 1")
            self.assertIn("--order: 3;", styles, "Should have kept the inline CSS variable")

        for classes, styles in [get_classes_styles("col2-with-changes"), get_classes_styles("col4-no-change")]:
            self.assertNotIn("order-0", classes, "Should not have a mobile order class")
            self.assertIn("order-lg-0", classes, "Should have an order-lg-0 class for desktops")
            self.assertIn("custom-order-2", classes, "Should have kept the custom-order-2 class")
            self.assertIn("order-4-custom", classes, "Should have kept the order-4-custom class")
            self.assertIn("order: 0;", styles, "Should have an inline style order: 0")
