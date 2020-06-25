# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import decimal

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase
from odoo.tools import float_repr
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
            % (
                (
                    """
                    LEFT JOIN mrp_bom bom
                           ON
                            (
                              bom.product_id = pp.id
                              OR (bom.product_tmpl_id = pt.id AND bom.product_id is NULL AND bom.type = 'phantom')
                            )
                    WHERE coalesce(bom.type, '') != 'phantom'
                """,
                    ", bom.product_id, bom.sequence",
                )
                if ignore_kits
                else ("", "")
            )
        )
        results = []
        for sub_ids in util.chunks((row[0] for row in self.env.cr.fetchall()), 10000, list):
            products = self.env["product.product"].browse(sub_ids)
            # If a product is created or deleted, this can lead to an issue.
            # So, only compare products having quantities != 0
            results += [
                [p.id, float_repr(p.qty_available, -decimal.Decimal(str(p.uom_id.rounding)).as_tuple().exponent)]
                for p in products
                if p.qty_available
            ]
        return [release.series, results]
