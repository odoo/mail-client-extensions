# -*- coding: utf-8 -*-

import decimal

from odoo import release
from odoo.tools import float_repr
from odoo.tools.parse_version import parse_version

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


class TestOnHandQuantityUnchanged(IntegrityCase):
    def check(self, value):
        before_version, before_results = value
        ignore_kits = "mrp.bom" in self.env.registry and parse_version(before_version) < parse_version("13.0")
        after_version, after_results = self.invariant(
            ignore_kits=ignore_kits, only_product_ids=[i for i, _ in before_results]
        )
        self.assertEqual(before_results, self.convert_check(after_results), self.message)

    def invariant(self, ignore_kits=False, only_product_ids=None):
        def trim_trailing_zeros(value):
            return value.rstrip("0").rstrip(".")

        ignore_kits = ignore_kits or (
            "mrp.bom" in self.env.registry and parse_version(release.series) < parse_version("13.0")
        )
        ignore_kits_query = ""
        where_clause = []
        where_params = []
        query = """
                SELECT pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                     AND pp.active = TRUE AND pt.TYPE = 'product'
                {ignore_kits_query}
                WHERE {where_clause}
                GROUP BY pp.id
                ORDER BY pp.id
            """
        if ignore_kits:
            ignore_kits_query = """
                LEFT JOIN LATERAL (
                    SELECT type
                    FROM mrp_bom
                    WHERE type = 'phantom'
                    AND (product_tmpl_id = pt.id OR product_id = pp.id)
                    LIMIT 1
                ) bom ON true"""
            where_clause += ["coalesce(bom.type, '') != 'phantom'"]

        if only_product_ids is not None:
            where_clause += ["pp.id = ANY(%s)"]
            where_params += [list(only_product_ids)]

        query = query.format(ignore_kits_query=ignore_kits_query, where_clause=" AND ".join(where_clause or ["true"]))
        self.env.cr.execute(query, where_params)
        results = []
        for sub_ids in util.chunks((row[0] for row in self.env.cr.fetchall()), 10000, list):
            self.env["product.product"].invalidate_cache()
            products = self.env["product.product"].browse(sub_ids)
            # If a product is created or deleted, this can lead to an issue.
            # So, only compare products having quantities != 0
            results += [
                [
                    p.id,
                    trim_trailing_zeros(
                        float_repr(p.qty_available, -decimal.Decimal(str(p.uom_id.rounding)).as_tuple().exponent)
                    ),
                ]
                for p in products
                if p.qty_available
            ]
        return [release.series, results]
