# -*- coding: utf-8 -*-
from odoo.tests import Form

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.4")
class TestQualityCheck(UpgradeCase):
    def prepare(self):
        uom_unit_id = self.env.ref("uom.product_uom_unit")
        product_category_id = self.env.ref("product.product_category_all")

        # Main Product
        product = self.env["product.product"].create(
            {"name": "Main Product", "type": "product", "categ_id": product_category_id.id}
        )

        # Components
        comp1 = self.env["product.product"].create(
            {"name": "Component 1", "type": "product", "categ_id": product_category_id.id}
        )
        comp2 = self.env["product.product"].create(
            {"name": "Component 2", "type": "product", "categ_id": product_category_id.id}
        )
        comp3 = self.env["product.product"].create(
            {"name": "Component 3", "type": "product", "categ_id": product_category_id.id}
        )
        comp4 = self.env["product.product"].create(
            {"name": "Component 4", "type": "product", "categ_id": product_category_id.id}
        )

        product.product_tmpl_id.tracking = "serial"
        comp1.product_tmpl_id.tracking = "serial"
        comp2.product_tmpl_id.tracking = "serial"
        comp3.product_tmpl_id.tracking = "serial"
        comp4.product_tmpl_id.tracking = "serial"

        # Routing
        routing = self.env["mrp.routing"].create({"name": "Rounting 1"})

        # Bill of Material
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_qty": 1.0,
                "routing_id": routing.id,
                "product_uom_id": uom_unit_id.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": comp1.id, "product_qty": 2, "product_uom_id": uom_unit_id.id}),
                    (0, 0, {"product_id": comp2.id, "product_qty": 2, "product_uom_id": uom_unit_id.id}),
                    (0, 0, {"product_id": comp3.id, "product_qty": 4, "product_uom_id": uom_unit_id.id}),
                    (0, 0, {"product_id": comp4.id, "product_qty": 4, "product_uom_id": uom_unit_id.id}),
                ],
            }
        )

        # Workcenter
        workcenter_id = self.env["mrp.workcenter"].create({"name": "Workcenter 1"})

        # Operations
        operation_1 = self.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 1",
                "routing_id": routing.id,
                "workcenter_id": workcenter_id.id,
                "time_cycle_manual": 30,
                "sequence": 20,
            }
        )
        operation_2 = self.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 2",
                "routing_id": routing.id,
                "workcenter_id": workcenter_id.id,
                "time_cycle_manual": 30,
                "sequence": 20,
            }
        )
        operation_3 = self.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 3",
                "routing_id": routing.id,
                "workcenter_id": workcenter_id.id,
                "time_cycle_manual": 30,
                "sequence": 20,
            }
        )

        # Picking Type
        picking_type_id = self.env["stock.picking.type"].create(
            {
                "name": "Manufacturing",
                "sequence_code": "MO",
                "code": "mrp_operation",
                "use_create_components_lots": True,
                "warehouse_id": self.env.ref("stock.warehouse0").id,
            }
        )

        # Control Points
        self.env["quality.point"].create(
            {
                "name": "QCP0001",
                "product_tmpl_id": product.product_tmpl_id.id,
                "picking_type_id": picking_type_id.id,
                "operation_id": operation_1.id,
            }
        )
        self.env["quality.point"].create(
            {
                "name": "QCP0002",
                "product_tmpl_id": product.product_tmpl_id.id,
                "picking_type_id": picking_type_id.id,
                "operation_id": operation_2.id,
            }
        )
        self.env["quality.point"].create(
            {
                "name": "QCP0003",
                "product_tmpl_id": product.product_tmpl_id.id,
                "picking_type_id": picking_type_id.id,
                "operation_id": operation_3.id,
            }
        )

        order = Form(self.env["mrp.production"])
        order.product_id = product
        order = order.save()
        order.action_confirm()
        order.button_plan()

        return {"check_without_production_ids": order.workorder_ids.check_ids.ids}

    def check(self, init):
        check_without_production_ids = self.env["quality.check"].browse(init["check_without_production_ids"])

        self.cr.execute(
            """
                SELECT DISTINCT(qc.production_id)
                  FROM mrp_workorder mw
                  JOIN quality_check qc ON mw.id = qc.workorder_id
                 WHERE qc.id in %s
            """,
            [tuple(check_without_production_ids.ids)],
        )
        check_production_id = self.cr.fetchone()

        for check in check_without_production_ids:
            production_id = check.production_id.id
            self.assertEqual(production_id, check_production_id[0])
