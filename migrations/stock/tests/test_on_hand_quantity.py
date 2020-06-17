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
        after_version, after_results = self.invariant(
            ignore_kits=ignore_kits, only_product_ids=[i for i, _ in before_results]
        )
        self.assertEqual(before_results, self.convert_check(after_results), self.message)

    def invariant(self, ignore_kits=False, only_product_ids=None):
        ignore_kits = ignore_kits or (
            "mrp.bom" in self.env.registry and parse_version(release.series) < parse_version("13.0")
        )
        self.env.cr.execute(
            """
                SELECT pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                AND pp.active = TRUE AND pt.TYPE = 'product'
                %s
                %s
                GROUP BY pp.id
                ORDER BY pp.id
            """
            % (
                """
                LEFT JOIN LATERAL (
                    SELECT type
                    FROM mrp_bom
                    WHERE type = 'phantom'
                    AND (product_tmpl_id = pt.id OR product_id = pp.id)
                    LIMIT 1
                ) bom ON true
                WHERE coalesce(bom.type, '') != 'phantom'
                """
                if ignore_kits
                else "",
                (
                    only_product_ids
                    and (
                        """
                %s pp.id IN %s
                    """
                        % ("AND" if ignore_kits else "WHERE", str(tuple(only_product_ids)))
                    )
                )
                or (only_product_ids is not None and "%s FALSE" % ("AND" if ignore_kits else "WHERE"))
                or "",
            )
        )
        results = []
        for sub_ids in util.chunks((row[0] for row in self.env.cr.fetchall()), 10000, list):
            self.env["product.product"].invalidate_cache()
            products = self.env["product.product"].browse(sub_ids)
            # If a product is created or deleted, this can lead to an issue.
            # So, only compare products having quantities != 0
            results += [
                [p.id, float_repr(p.qty_available, -decimal.Decimal(str(p.uom_id.rounding)).as_tuple().exponent)]
                for p in products
                if p.qty_available
            ]
        return [release.series, results]
