# -*- coding: utf-8 -*-
from odoo.tests import Form

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~12.4")
class Testqualitycheck(UpgradeCase):
    def prepare(self):
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_category_all = self.env.ref("product.product_category_all")

        product = self.env["product.product"].create(
            {"name": "Product1", "type": "product", "categ_id": product_category_all.id}
        )
        comp1 = self.env["product.product"].create(
            {"name": "comp1", "type": "product", "categ_id": product_category_all.id}
        )
        comp2 = self.env["product.product"].create(
            {"name": "comp2", "type": "product", "categ_id": product_category_all.id}
        )
        comp3 = self.env["product.product"].create(
            {"name": "comp3", "type": "product", "categ_id": product_category_all.id}
        )
        comp4 = self.env["product.product"].create(
            {"name": "comp4", "type": "product", "categ_id": product_category_all.id}
        )
        by_product1 = self.env["product.product"].create(
            {"name": "By Product1", "type": "product", "categ_id": product_category_all.id}
        )
        by_product2 = self.env["product.product"].create(
            {"name": "By Product2", "type": "product", "categ_id": product_category_all.id}
        )

        product.product_tmpl_id.tracking = "lot"
        comp1.product_tmpl_id.tracking = "lot"
        comp2.product_tmpl_id.tracking = "lot"
        comp3.product_tmpl_id.tracking = "lot"
        comp4.product_tmpl_id.tracking = "lot"
        by_product1.product_tmpl_id.tracking = "lot"
        by_product2.product_tmpl_id.tracking = "lot"

        workcenter1 = self.env["mrp.workcenter"].create({"name": "Test1"})

        routing = self.env["mrp.routing"].create(
            {
                "name": "rounting1",
                "operation_ids": [
                    (0, 0, {"workcenter_id": workcenter1.id, "name": "Test1", "time_cycle_manual": 30, "sequence": 20})
                ],
            }
        )
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "routing_id": routing.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": comp1.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": comp2.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": comp3.id, "product_qty": 0, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": comp4.id, "product_qty": 0, "product_uom_id": uom_unit.id}),
                ],
                "byproduct_ids": [
                    (0, 0, {"product_id": by_product1.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": by_product2.id, "product_qty": 0, "product_uom_id": uom_unit.id}),
                ],
            }
        )
        order = Form(self.env["mrp.production"])
        order.product_id = product
        order = order.save()
        if util.version_gte("saas~12.1"):
            order.action_confirm()
        order.button_plan()

        workorder_id = order.workorder_ids.check_ids
        check_ids = []
        check_without_move_ids = []
        for qc in workorder_id:
            check_id = qc.id
            check_ids.append(check_id)
            move_id = qc.move_line_id
            if not move_id:
                check_without_move_ids.append(check_id)
        return {
            "check_ids": check_ids,
            "check_without_move_ids": check_without_move_ids,
        }

    def check(self, init):
        quality_check = self.env["quality.check"].browse(init["check_ids"])
        check_without_move_ids = self.env["quality.check"].browse(init["check_without_move_ids"])

        self.cr.execute(
            """
            SELECT distinct(wl.id)
              FROM mrp_workorder_line wl
              JOIN stock_move m ON m.id = wl.move_id,
                   quality_check qc, mrp_production mp
             WHERE qc.workorder_id = wl.raw_workorder_id
               AND wl.qty_done = 0
               AND m.raw_material_production_id IS NOT NULL
               AND qc.product_id = mp.product_id
               AND m.state not in ('done', 'cancel')
        """
        )
        line_id = self.cr.fetchone()

        for qc in quality_check:
            workorder_ids = qc.workorder_line_id
            self.assertTrue(workorder_ids.exists())

        for id in check_without_move_ids:
            workorder_id = id.workorder_line_id
            self.assertEqual(workorder_id.id, line_id[0])
