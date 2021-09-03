# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@change_version("saas~12.4")
class TestDisplayLines(UpgradeCase):
    def prepare(self):
        # Setup products.
        env = self.env
        unit = env.ref("uom.product_uom_unit")
        uoms = dict(uom_id=unit.id, uom_po_id=unit.id)

        product1 = env["product.product"].create({"name": "Product 1", **uoms})
        product2 = env["product.product"].create({"name": "Product 2", **uoms})

        sale_order_lines = [
            (
                0,
                0,
                {
                    "name": "order_line_1",
                    "display_type": "line_section",
                    "product_uom_qty": 0.0,
                    "price_unit": 0.0,
                },
            ),
            (
                0,
                0,
                {
                    "name": "order_line_2",
                    "product_id": product1.id,
                    "product_uom_qty": 2.0,
                    "price_unit": 1000.0,
                    "product_uom": unit.id,
                },
            ),
            (
                0,
                0,
                {
                    "name": "order_line_3",
                    "display_type": "line_section",
                    "product_uom_qty": 0.0,
                    "price_unit": 0.0,
                },
            ),
            (
                0,
                0,
                {
                    "name": "order_line_4",
                    "product_id": product2.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 2400,
                    "product_uom": unit.id,
                },
            ),
            (
                0,
                0,
                {
                    "name": "order_line_5",
                    "display_type": "line_note",
                    "product_uom_qty": 0.0,
                    "price_unit": 0.0,
                },
            ),
        ]
        partner = env.ref("base.partner_admin")
        sale_order = env["sale.order"].create(
            {
                "name": "Test Sale Order",
                "partner_id": partner.id,
                "order_line": sale_order_lines,
            }
        )
        sale_order.action_confirm()
        for line in sale_order.order_line.filtered(lambda l: l.product_id):
            line.write({"qty_delivered": line.product_uom_qty})
        sale_order._create_invoices()
        with no_fiscal_lock(self.env.cr):
            sale_order.invoice_ids.action_invoice_open()

        return {"test_invoice_move_id": sale_order.invoice_ids.move_id.id}

    def check(self, init):
        self.cr.execute(
            """
            SELECT count(*)
              FROM account_move_line
             WHERE display_type IS NOT NULL
               AND move_id = %s
            """,
            [init["test_invoice_move_id"]],
        )
        no_of_display_lines = self.cr.fetchone()
        self.cr.execute(
            """
            SELECT count(rel.*)
              FROM sale_order_line_invoice_rel rel
              JOIN account_move_line aml ON aml.id = rel.invoice_line_id
              JOIN account_move am ON am.id = aml.move_id
             WHERE aml.display_type IS NOT NULL
               AND am.id = %s
            """,
            [init["test_invoice_move_id"]],
        )
        self.assertEqual(no_of_display_lines, self.cr.fetchone())
