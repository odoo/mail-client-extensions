import contextlib
import decimal

from odoo import models, release
from odoo.tools import float_repr

with contextlib.suppress(ImportError):
    from odoo.tools import SQL

from odoo.tools.parse_version import parse_version

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase, UpgradeCase

if util.version_gte("15.0"):

    class ProductProduct(models.Model):
        _name = "product.product"
        _inherit = "product.product"
        # The reason to use mrp here is twofold:
        # * The mismatch in ordering by product_id happens on mrp when searching the boms
        # * This override won't work for `_modele = "stock"` since the module is already
        #   loaded at the moment this file is loaded.
        # For the details on why this override is needed see the commit message
        _module = "mrp"

        if util.version_gte("17.0"):

            def _order_to_sql(self, order, query, alias=None, reverse=False):
                sql_order = super()._order_to_sql(order, query, alias, reverse)
                terms = self.env.cr.mogrify(sql_order).decode().split(",")
                return SQL(", ").join(SQL(term) for term in ensure_nulls_order(terms))

        else:

            def _generate_order_by_inner(self, alias, order_spec, query, reverse_direction=False, seen=None):
                terms = super()._generate_order_by_inner(alias, order_spec, query, reverse_direction, seen)
                return list(ensure_nulls_order(terms))

    def ensure_nulls_order(terms):
        for item in terms:
            field, _, direction = item.strip().rpartition(" ")
            if field.split(".")[-1].strip("'\"") == "priority":
                nullorder = "LAST" if direction == "DESC" else "FIRST"
                yield item + " NULLS " + nullorder
            else:
                yield item


class TestOnHandQuantityUnchanged_Prepare(UpgradeCase):
    def prepare(self):
        if util.version_gte("saas~17.3"):
            product_material = self.env["product.product"].create({"name": "Material", "is_storable": True})
        else:
            product_material = self.env["product.product"].create({"name": "Material", "type": "product"})
        warehouse_1 = self.env.ref("stock.warehouse0")
        company_2 = self.env["res.company"].create({"name": "Company_wh2"})
        warehouse_2 = self.env["stock.warehouse"].create(
            {"name": "WH 2", "code": "WH2", "company_id": company_2.id, "partner_id": company_2.partner_id.id}
        )
        self.env["stock.quant"].create(
            [
                {"product_id": product_material.id, "location_id": warehouse_1.lot_stock_id.id, "quantity": 1},
                {"product_id": product_material.id, "location_id": warehouse_2.lot_stock_id.id, "quantity": 2},
            ]
        )
        return {}

    def check(self, init):
        # only prepare since we only want to inject data for TestOnHandQuantityUnchanged
        pass


class TestOnHandQuantityUnchanged(IntegrityCase):
    def check(self, value):
        before_version, before_results = value
        before_version = parse_version(before_version)
        ignore_kits = "mrp.bom" in self.env.registry and before_version < parse_version("13.0")
        warehouses = (
            self.env["stock.warehouse"].search([])
            if (
                before_version < parse_version("15.0")  # target of the backported patch
                or before_version in (parse_version("saas~15.2"), parse_version("saas~16.2"))  # skipped forward ports
            )
            else None
        )
        after_version, after_results = self.invariant(
            ignore_kits=ignore_kits, only_product_ids=[i for i, _ in before_results], warehouses=warehouses
        )
        self.assertEqual(before_results, self.convert_check(after_results), self.message)

    @util.no_selection_cache_validation
    def invariant(self, ignore_kits=False, only_product_ids=None, warehouses=None):
        self.skip_if_demo()

        def trim_trailing_zeros(value):
            return value.rstrip("0").rstrip(".")

        ignore_kits = ignore_kits or (
            "mrp.bom" in self.env.registry and parse_version(release.series) < parse_version("13.0")
        )
        ignore_kits_query = ""
        where_clause = []
        where_params = []
        sql_pt_join_clause = "pt.is_storable = TRUE" if util.version_gte("saas~17.3") else "pt.type = 'product'"
        query = """
                SELECT pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    AND pp.active = TRUE AND {sql_pt_join_clause}
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

        query = query.format(
            sql_pt_join_clause=sql_pt_join_clause,
            ignore_kits_query=ignore_kits_query,
            where_clause=" AND ".join(where_clause or ["true"]),
        )
        self.env.cr.execute(query, where_params)
        results = []
        for sub_ids in util.chunks((row[0] for row in self.env.cr.fetchall()), 10000, list):
            util.invalidate(self.env["product.product"])
            products = self.env["product.product"].with_context(warehouse=warehouses and warehouses.ids).browse(sub_ids)
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
