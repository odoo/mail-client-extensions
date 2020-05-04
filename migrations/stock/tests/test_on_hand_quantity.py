# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import IntegrityCase
from odoo.tools.parse_version import parse_version
from odoo import release


class TestOnHandQuantityUnchanged(IntegrityCase):
    def check(self, value):
        before_version, before_results = value
        ignore_kits = "mrp.bom" in self.env.registry and parse_version(before_version) < parse_version("13.0")
        after_version, after_results = self.invariant(ignore_kits=ignore_kits)
        self.assertEqual(before_results, self.convert_check(after_results), self.message)

    def invariant(self, ignore_kits=False):
        ignore_kits = ignore_kits or (
            "mrp.bom" in self.env.registry and parse_version(release.series) < parse_version("13.0")
        )
        self.env.cr.execute(
            """
                SELECT DISTINCT ON (pp.id) pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                AND pp.active = TRUE AND pt.TYPE = 'product'
                %s
                ORDER BY pp.id%s
            """
            % ((
                """
                    LEFT JOIN mrp_bom bom ON bom.product_id = pp.id OR bom.product_tmpl_id = pt.id
                    WHERE coalesce(bom.type, '') != 'phantom'
                """, ", bom.sequence"
            ) if ignore_kits else ("", ""))
        )
        products = self.env["product.product"].browse([row[0] for row in self.env.cr.fetchall()])
        results = products.mapped(lambda p: [p.id, p.qty_available])
        return [release.series, results]
