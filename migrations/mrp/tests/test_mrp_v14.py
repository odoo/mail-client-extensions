# -*- coding: utf-8 -*-

from odoo.tests import Form, tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@tagged("mrp_v14")
@change_version("saas~13.4")
class TestBackorders(UpgradeCase):
    def prepare(self):
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_category_all = self.env.ref("product.product_category_all")

        # ---------------------------------------------------------------------
        # order1: no tracking and no routing, unique production, done MO
        # ---------------------------------------------------------------------
        bom1finished1 = self.env["product.product"].create(
            {"name": "bom1finished1", "type": "product", "categ_id": product_category_all.id}
        )
        bom1comp1 = self.env["product.product"].create(
            {"name": "bom1comp1", "type": "product", "categ_id": product_category_all.id}
        )
        bom1comp2 = self.env["product.product"].create(
            {"name": "bom1comp2", "type": "product", "categ_id": product_category_all.id}
        )
        bom1 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom1finished1.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom1comp1.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": bom1comp2.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                ],
            }
        )

        order1 = Form(self.env["mrp.production"])
        order1.product_id = bom1finished1
        order1.bom_id = bom1
        order1.product_qty = 2
        order1 = order1.save()
        order1.action_confirm()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order1.id, "active_ids": [order1.id]})
        )
        produce1.qty_producing = 2.0
        produce1 = produce1.save()
        produce1.do_produce()
        order1.button_mark_done()

        self.assertEqual(order1.state, "done")
        self.assertEqual(len(order1.move_raw_ids), 2)
        self.assertEqual(order1.move_raw_ids.mapped("product_qty"), [2, 2])

        # ---------------------------------------------------------------------
        # order2: no tracking and no routing, multiple productions, done MO
        # ---------------------------------------------------------------------
        order2 = Form(self.env["mrp.production"])
        order2.product_id = bom1finished1
        order2.bom_id = bom1
        order2.product_qty = 2
        order2 = order2.save()
        order2.action_confirm()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order2.id, "active_ids": [order2.id]})
        )
        produce1.qty_producing = 1.0
        produce1 = produce1.save()
        produce1.do_produce()
        order2.post_inventory()
        produce2 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order2.id, "active_ids": [order2.id]})
        )
        produce2.qty_producing = 1.0
        produce2 = produce2.save()
        produce2.do_produce()
        order2.button_mark_done()

        self.assertEqual(order2.state, "done")
        self.assertEqual(len(order2.move_raw_ids), 4)
        self.assertEqual(order2.move_raw_ids.mapped("product_qty"), [1, 1, 1, 1])
        self.assertEqual(len(order2.move_finished_ids), 2)
        self.assertEqual(order2.move_finished_ids.mapped("product_qty"), [1, 1])

        # ---------------------------------------------------------------------
        # order3: finished tracked by lot, no routing, unique production, done MO
        # ---------------------------------------------------------------------
        bom2finished1 = self.env["product.product"].create(
            {"name": "bom2finished1", "type": "product", "categ_id": product_category_all.id, "tracking": "lot"}
        )
        bom2comp1 = self.env["product.product"].create(
            {"name": "bom2comp1", "type": "product", "categ_id": product_category_all.id}
        )
        bom2comp2 = self.env["product.product"].create(
            {"name": "bom2comp2", "type": "product", "categ_id": product_category_all.id}
        )
        bom2 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom2finished1.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom2comp1.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": bom2comp2.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                ],
            }
        )
        lot1 = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": bom2finished1.id,
                "company_id": self.env.company.id,
            }
        )

        order3 = Form(self.env["mrp.production"])
        order3.product_id = bom2finished1
        order3.bom_id = bom2
        order3.product_qty = 2
        order3 = order3.save()
        order3.action_confirm()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order3.id, "active_ids": [order3.id]})
        )
        produce1.qty_producing = 2.0
        produce1.finished_lot_id = lot1
        produce1 = produce1.save()
        produce1.do_produce()
        order3.button_mark_done()

        self.assertEqual(order3.state, "done")
        self.assertEqual(len(order3.move_raw_ids), 2)
        self.assertEqual(order3.move_raw_ids.mapped("product_qty"), [2, 2])
        # ---------------------------------------------------------------------
        # order4: finished tracked by lot, no routing, multiple productions, done MO
        # ---------------------------------------------------------------------
        nb_qty_order4 = 6
        lots_finished = []
        for i in range(nb_qty_order4):
            lots_finished.append(
                {
                    "name": "lot_order4_%s" % i,
                    "product_id": bom2finished1.id,
                    "company_id": self.env.company.id,
                }
            )
        lots_finished = self.env["stock.production.lot"].create(lots_finished)
        order4 = Form(self.env["mrp.production"])
        order4.product_id = bom2finished1
        order4.bom_id = bom2
        order4.product_qty = nb_qty_order4
        order4 = order4.save()
        order4.action_confirm()
        for i in range(nb_qty_order4):
            produce1 = Form(
                self.env["mrp.product.produce"].with_context({"active_id": order4.id, "active_ids": [order4.id]})
            )
            produce1.qty_producing = 1.0
            produce1.finished_lot_id = lots_finished[i]
            produce1 = produce1.save()
            produce1.do_produce()
            if i % 2 == 0:  # Don't Post the inventory every time
                order4.post_inventory()

        order4.button_mark_done()

        self.assertEqual(order4.state, "done")
        self.assertEqual(sum(order4.move_raw_ids.mapped("product_uom_qty")), nb_qty_order4 * 2)
        self.assertEqual(order4.qty_produced, nb_qty_order4)

        # ---------------------------------------------------------------------
        # order5: no tracked, no routing, multiple productions, MO in progress
        # ---------------------------------------------------------------------
        order5 = Form(self.env["mrp.production"])
        order5.product_id = bom1finished1
        order5.bom_id = bom1
        order5.product_qty = 3
        order5 = order5.save()
        order5.action_confirm()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order5.id, "active_ids": [order5.id]})
        )
        produce1.qty_producing = 1.0
        produce1 = produce1.save()
        produce1.do_produce()
        order5.post_inventory()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order5.id, "active_ids": [order5.id]})
        )
        produce1.qty_producing = 1.0
        produce1 = produce1.save()
        produce1.do_produce()

        self.assertEqual(order5.state, "progress")
        self.assertEqual(sum(order5.move_raw_ids.mapped("product_uom_qty")), 6)
        self.assertEqual(sum(order5.move_raw_ids.move_line_ids.mapped("qty_done")), 4)
        self.assertEqual(order5.qty_produced, 2)

        # ---------------------------------------------------------------------
        # order6: no tracked, no routing, multiple productions, MO in progress
        # ---------------------------------------------------------------------
        order6 = Form(self.env["mrp.production"])
        order6.product_id = bom1finished1
        order6.bom_id = bom1
        order6.product_qty = 3
        order6 = order6.save()
        order6.action_confirm()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order6.id, "active_ids": [order6.id]})
        )
        produce1.qty_producing = 1.0
        produce1 = produce1.save()
        produce1.do_produce()
        produce1 = Form(
            self.env["mrp.product.produce"].with_context({"active_id": order6.id, "active_ids": [order6.id]})
        )
        produce1.qty_producing = 1.0
        produce1 = produce1.save()
        produce1.do_produce()

        self.assertEqual(order6.state, "progress")
        self.assertEqual(sum(order6.move_raw_ids.mapped("product_uom_qty")), 6)
        self.assertEqual(sum(order6.move_raw_ids.move_line_ids.mapped("qty_done")), 4)
        self.assertEqual(order6.qty_produced, 2)

        # ---------------------------------------------------------------------
        # order7: Focus on UoM issue
        # ---------------------------------------------------------------------

        return {
            "order1": {"id": order1.id, "lots_produced": [], "qties_produced": [2]},
            "order2": {"id": order2.id, "lots_produced": [], "qties_produced": [1, 1]},
            "order3": {"id": order3.id, "lots_produced": [lot1.id], "qties_produced": [2]},
            "order4": {"id": order4.id, "lots_produced": lots_finished.ids, "qties_produced": [1] * nb_qty_order4},
            "order5": {"id": order5.id, "lots_produced": [], "qties_produced": 2},
            "order6": {"id": order6.id, "lots_produced": [], "qties_produced": 2},
        }

    def check(self, init):
        # order1: no backorder, qty_producing set correctly, remain unchanged
        order1 = self.env["mrp.production"].browse(init["order1"]["id"])
        self.assertEqual(len(order1.procurement_group_id.mrp_production_ids), 1)
        self.assertEqual(order1.state, "done")
        self.assertEqual(len(order1.move_raw_ids), 2)
        self.assertEqual(order1.move_raw_ids.mapped("product_qty"), [2, 2])
        self.assertEqual(order1.qty_produced, 2)
        self.assertEqual(order1.qty_producing, 2)

        # order2: no backorder, qty_producing set correctly, remain unchanged
        order2 = self.env["mrp.production"].browse(init["order2"]["id"])
        self.assertEqual(len(order2.procurement_group_id.mrp_production_ids), 1)
        self.assertEqual(order2.state, "done")
        self.assertEqual(len(order2.move_raw_ids), 4)
        self.assertEqual(order2.move_raw_ids.mapped("product_qty"), [1, 1, 1, 1])
        self.assertEqual(len(order2.move_finished_ids), 2)
        self.assertEqual(order2.move_finished_ids.mapped("product_qty"), [1, 1])
        self.assertEqual(order2.qty_produced, 2)
        self.assertEqual(order2.qty_producing, 2)

        # order3: no backorder and lot, qty_producing set correctly, remain unchanged
        order3 = self.env["mrp.production"].browse(init["order3"]["id"])
        self.assertEqual(len(order3.procurement_group_id.mrp_production_ids), 1)
        self.assertEqual(order3.state, "done")
        self.assertEqual(len(order3.move_raw_ids), 2)
        self.assertEqual(order3.move_raw_ids.mapped("product_qty"), [2, 2])
        self.assertEqual(order3.lot_producing_id.id, init["order3"]["lots_produced"][0])
        self.assertEqual(order3.qty_producing, init["order3"]["qties_produced"][0])

        # order4: backorders and lot
        order4 = self.env["mrp.production"].browse(init["order4"]["id"])
        self.assertEqual(len(order4.procurement_group_id.mrp_production_ids), len(init["order4"]["lots_produced"]))
        self.assertEqual(
            sum(order4.procurement_group_id.mrp_production_ids.mapped("product_qty")),
            sum(init["order4"]["qties_produced"]),
        )

        self.assertEqual(
            set(order4.procurement_group_id.mrp_production_ids.lot_producing_id.ids),
            set(init["order4"]["lots_produced"]),
        )
        for index in range(len(init["order4"]["lots_produced"])):
            backorder = order4.procurement_group_id.mrp_production_ids[index]
            self.assertEqual(backorder.qty_producing, init["order4"]["qties_produced"][index])
            self.assertEqual(backorder.move_raw_ids.move_dest_ids, order4.move_raw_ids.move_dest_ids)
            self.assertEqual(backorder.move_raw_ids.move_orig_ids, order4.move_raw_ids.move_orig_ids)
            self.assertEqual(backorder.move_raw_ids.mapped("product_qty"), [1, 1])

        order5 = self.env["mrp.production"].browse(init["order5"]["id"])
        self.assertEqual(order5.state, "done")
        self.assertEqual(order5.qty_producing, 1)
        self.assertEqual(order5.qty_produced, 1)
        self.assertEqual(order5.move_raw_ids.mapped("product_qty"), [1, 1])
        self.assertEqual(len(order5.procurement_group_id.mrp_production_ids), 2)
        # Backorder due to the post inventory
        backorder = order5.procurement_group_id.mrp_production_ids[-1]
        self.assertEqual(backorder.state, "progress")
        self.assertEqual(backorder.qty_producing, 1)
        self.assertEqual(backorder.product_qty, 2)
        self.assertEqual(backorder.move_raw_ids.mapped("quantity_done"), [1, 1])

        order6 = self.env["mrp.production"].browse(init["order6"]["id"])
        self.assertEqual(len(order6.procurement_group_id.mrp_production_ids), 1)
        self.assertEqual(order6.state, "progress")
        self.assertEqual(order6.qty_producing, 2)
        self.assertEqual(order6.qty_produced, 0)  # stock move line will be recreate at "Mark as Done"
        self.assertEqual(order6.move_raw_ids.mapped("quantity_done"), [2, 2])
        self.assertEqual(sum(order6.move_raw_ids.mapped("product_uom_qty")), 6)
