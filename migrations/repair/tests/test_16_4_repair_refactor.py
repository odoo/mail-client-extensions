# -*- coding: utf-8 -*-
import contextlib
from datetime import date, timedelta

with contextlib.suppress(ImportError):  # Command not available < 16.0, (but this file is not necessary anyway)
    from odoo import Command

from odoo.tools import float_compare

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.4")
class TestRepairRefactor(UpgradeCase):
    def prepare(self):
        company_id = self.env.company.id
        product_values = [
            {
                "name": "Lot Product",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "tracking": "lot",
            },
            {
                "name": "Serial Product",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "tracking": "serial",
            },
            {
                "name": "None Product",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "tracking": "none",
            },
        ]

        customer = self.env["res.partner"].create(
            {
                "name": "Deco Addict",
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "zip": "94523",
                "country_id": self.env.ref("base.us").id,
            }
        )

        product_ids = self.env["product.product"].create(product_values)
        lot_product, serial_product, none_product = product_ids
        quant = self.env["stock.quant"]
        for product in product_ids:
            quant |= self.create_quant(product, 10)
        quant.action_apply_inventory()

        lot_id = self.env["stock.lot"].search_read([("product_id", "=", lot_product.id)], ["id"])[0]["id"]
        serial_ids = [
            x["id"]
            for x in self.env["stock.lot"].search_read(
                [("product_id", "=", serial_product.id)], ["id"], order="id DESC"
            )
        ]

        stock_location_id = self.env.ref("stock.stock_location_stock").id
        prod_location_id = (
            self.env["stock.location"]
            .search([("usage", "=", "production"), ("company_id", "=", company_id)], limit=1)
            .id
        )
        scrap_location_id = (
            self.env["stock.location"]
            .search([("scrap_location", "=", True), ("company_id", "in", [company_id, False])], limit=1)
            .id
        )

        r_tags = self.env["repair.tags"].create(
            [
                {
                    "name": "01",
                },
                {
                    "name": "02",
                },
                {
                    "name": "03",
                },
                {
                    "name": "04",
                },
                {
                    "name": "05",
                },
            ]
        )
        r_tags = {tag.name: tag.id for tag in r_tags}
        # prepare and check tests may happen on two different days :
        today = date.today()  # ensure it remains constant
        day_delta = timedelta(days=2)  # may break the tests with a lesser value
        repair_values = [
            {  # 01
                "tag_ids": [
                    Command.link(r_tags["01"]),
                ],
                "product_id": lot_product.id,
                "product_qty": 2.0,
                "lot_id": lot_id,
                "location_id": stock_location_id,
                "invoice_method": "none",
                "guarantee_limit": today - day_delta,
                "operations": [  # => lock_location
                    Command.create(
                        {
                            "name": "line 1",
                            "type": "add",
                            "product_id": none_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 1.0,
                            "location_id": stock_location_id,
                            "location_dest_id": prod_location_id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "2 serial, 1 lot_id",
                            "type": "add",
                            "product_id": serial_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 2.0,
                            "lot_id": serial_ids.pop(),  # In old model, whenever we can assign a qty > 1 to a serial product, lot_id remains a M2O.
                            "location_id": stock_location_id,
                            "location_dest_id": scrap_location_id,  # As 'add' repair line type is associated to various locations, location edition shall be locked (RO's state => 'confirmed')
                        }
                    ),
                ],
            },
            {  # 02
                "tag_ids": [
                    Command.link(r_tags["02"]),
                ],
                "product_id": serial_product.id,
                "product_qty": 1.0,
                "lot_id": serial_ids.pop(),
                "location_id": stock_location_id,
                "invoice_method": "b4repair",
                "partner_id": customer.id,
            },
            {  # 03
                "tag_ids": [
                    Command.link(r_tags["03"]),
                ],
                "product_id": none_product.id,
                "product_qty": 2.0,
                "location_id": stock_location_id,
                "invoice_method": "b4repair",
                "partner_id": customer.id,
                "guarantee_limit": today + day_delta,
                "operations": [
                    Command.create(
                        {
                            "name": "serial same lot_id",
                            "type": "add",
                            "product_id": serial_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 1.0,
                            "lot_id": serial_ids[-1],
                            "location_id": stock_location_id,
                            "location_dest_id": prod_location_id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "serial same lot_id",
                            "type": "add",
                            "product_id": serial_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 1.0,
                            "lot_id": serial_ids.pop(),
                            "location_id": stock_location_id,
                            "location_dest_id": prod_location_id,
                        }
                    ),
                ],
            },
            {  # 04
                "tag_ids": [
                    Command.link(r_tags["04"]),
                ],
                "product_id": none_product.id,
                "product_qty": 1.0,
                "location_id": stock_location_id,
                "invoice_method": "after_repair",
                "partner_id": customer.id,
                "guarantee_limit": today,
                "operations": [
                    Command.create(
                        {
                            "name": "1 serial, no lot_id",
                            "type": "add",
                            "product_id": serial_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 1.0,
                            "lot_id": serial_ids.pop(),
                            "location_id": stock_location_id,
                            "location_dest_id": prod_location_id,
                        }
                    ),
                ],
            },
            {  # 05
                "tag_ids": [
                    Command.link(r_tags["05"]),
                ],
                "product_id": none_product.id,
                "product_qty": 1.0,
                "location_id": stock_location_id,
                "invoice_method": "none",
                "guarantee_limit": today - day_delta,
                "operations": [
                    Command.create(
                        {
                            "name": "1 serial, 1 lot_id",
                            "type": "add",
                            "product_id": serial_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 1.0,
                            "lot_id": serial_ids.pop(),
                            "location_id": stock_location_id,
                            "location_dest_id": scrap_location_id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "n lot, 1 lot_id",
                            "type": "add",
                            "product_id": lot_product.id,
                            "price_unit": 0.5,
                            "product_uom_qty": 3.0,
                            "lot_id": lot_id,
                            "location_id": stock_location_id,
                            "location_dest_id": prod_location_id,
                        }
                    ),
                ],
            },
        ]
        repair_orders = self.env["repair.order"].create(repair_values)
        ro = {ro.tag_ids[0].name: ro for ro in repair_orders}

        # When upgrading a fresh installation without demo data,
        # [repair_order].action_repair_invoice_create() raises
        # an exception when it reach [account.move]._search_default_journal()
        # as there's no default accounting journal for sale operations
        company_id = self.env.company
        cur_id = company_id.currency_id.id
        domain = [("company_id", "=", company_id.id), ("type", "=", "sale")]
        journal = self.env["account.journal"].search_count(domain, limit=1)
        if not journal:
            self.env["account.journal"].create(
                {
                    "name": "Sale Journal",
                    "code": "INV",
                    "type": "sale",
                    "company_id": company_id.id,
                    "currency_id": cur_id,
                }
            )

        # state changes
        ro["02"].action_validate()
        ro["03"].action_validate()
        ro["04"].action_validate()
        ro["05"].action_validate()
        ro["02"].action_repair_invoice_create()
        (ro["04"] + ro["05"]).action_repair_start()
        (ro["04"] + ro["05"]).action_repair_end()

        # pre-test : assert state of 'old' ROs
        self.assertEqual(ro["01"].state, "draft")
        self.assertEqual(ro["02"].state, "ready")
        self.assertEqual(ro["03"].state, "2binvoiced")
        self.assertEqual(ro["04"].state, "2binvoiced")
        self.assertEqual(ro["05"].state, "done")
        self.assertNotEqual(len(repair_orders.operations.move_id), 0)

        return {
            "repair_ids": repair_orders.ids,
            "last_move_id": max(repair_orders.operations.move_id.ids),
            "date": today.isoformat(),
        }

    def check(self, init):
        Ro = self.env["repair.order"]
        repair_ids = init["repair_ids"]
        last_move_id = init["last_move_id"]
        same_date = date.fromisoformat(init["date"]) == date.today()

        # General checks
        missing_picking = Ro.search_count([("picking_type_id", "=", False)], 1)
        self.assertEqual(missing_picking, 0)
        assigned_so = Ro.search_count([("sale_order_id", "!=", False)], 1)
        self.assertEqual(assigned_so, 0)

        # UC checks
        repair_orders = Ro.browse(repair_ids)
        test_tags = {
            "01": [
                "s_confirmed",
                "w_false",
                "new_move",
                "forced_move_line",
            ],
            "02": [
                "s_confirmed",
                "w_false",
                "no_line",
                "serial_product",
            ],
            "03": [
                "s_draft",
                "w_true",
                "new_move",
            ],
            "04": [
                "s_under_repair",
                "existing_move",
            ],
            "05": [
                "w_true",
                "existing_move",
            ],
        }

        if same_date:
            """
            in old model, the field 'guarantee_limit' was a date,
            in new model, the replacing field 'under_warranty' is a boolean.
            if not same_date (prepare() on day D and check() on day D+1),
            we can't know if the migration of the field occuring in-between was done on day D or D+1
            such that we dont know if we must test w_true (day D) or w_false (day D +1)
            """
            test_tags["04"].append("w_true")

        for ro in repair_orders:
            tag_name = ro.tag_ids[0].name
            tests = test_tags[tag_name]
            if "w_true" in tests:
                self.assertTrue(ro.under_warranty)
            elif "w_false" in tests:
                self.assertFalse(ro.under_warranty)

            if "s_confirmed" in tests:
                self.assertEqual(ro.state, "confirmed")
            elif "s_draft" in tests:
                self.assertEqual(ro.state, "draft")
            elif "s_under_repair" in tests:
                self.assertEqual(ro.state, "under_repair")

            if "no_line" in tests:
                self.assertEqual(len(ro.move_ids), 0)
            elif "new_move" in tests:
                self.assertTrue(all(m.id > last_move_id for m in ro.move_ids))
            elif "existing_move" in tests:
                self.assertTrue(all(m.id <= last_move_id for m in ro.move_ids))

            if "serial_product" in tests:
                self.assertNotEqual(len(ro.lot_id), 0)

            if "forced_move_line" in tests:
                for move in ro.move_ids:
                    if not move.repair_line_type or move.has_tracking == "none":
                        continue
                    self.assertEqual(len(move.move_line_ids), 3)
                    self.assertEqual(len(move.move_line_ids.lot_id), 2)
                    self.assertEqual(float_compare(move.move_lines_count, move.product_uom_qty + 1, 2), 0)

            if tag_name == "04":
                try:
                    ro.action_repair_end()
                except Exception:
                    self.fail("action_repair_end() raised an Exception unexpectedly!")
                ro.under_warranty = False  # keeping it true would force SO prices to 0
                ro.action_create_sale_order()
                self.assertTrue(
                    all(float_compare(line.price_unit, 0.5, 2) == 0 for line in ro.sale_order_id.order_line)
                )

    def create_quant(self, product, qty, offset=0, location_id=None):
        if not location_id:
            location_id = self.env.ref("stock.stock_location_stock").id
        name = "L"
        i = 1
        if product.tracking == "serial":
            i, qty = qty, 1
            name = "S"

        vals = []
        for x in range(1, i + 1):
            qDict = {
                "location_id": location_id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }

            if product.tracking != "none":
                qDict["lot_id"] = (
                    self.env["stock.lot"]
                    .create(
                        {"name": name + str(offset + x), "product_id": product.id, "company_id": self.env.company.id}
                    )
                    .id
                )
            vals.append(qDict)

        return self.env["stock.quant"].create(vals)
