# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import release
from odoo.tests import Form, tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@tagged("mrp_v14")
@change_version("saas~13.4")
class TestRoutingQualityWorkorder(UpgradeCase):
    def prepare(self):
        if release.series != "13.3":
            return {}
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_category_all = self.env.ref("product.product_category_all")

        final_finished_1 = self.env["product.product"].create(
            {"name": "Phasesabers", "type": "product", "categ_id": product_category_all.id, "tracking": "serial"}
        )
        final_comp_1 = self.env["product.product"].create(
            {"name": "Phaseblade", "type": "product", "categ_id": product_category_all.id, "tracking": "serial"}
        )
        final_comp_2 = self.env["product.product"].create(
            {"name": "Crystal Shard", "type": "product", "categ_id": product_category_all.id}
        )
        workcenter1 = self.env["mrp.workcenter"].create({"name": "Craft Table"})
        workcenter2 = self.env["mrp.workcenter"].create({"name": "WorkcenterSaber"})

        final_routing = self.env["mrp.routing"].create({"name": "Saber Assembly"})

        mrp_routing_workcenter_0 = self.env["mrp.routing.workcenter"].create(
            {
                "routing_id": final_routing.id,
                "workcenter_id": workcenter1.id,
                "name": "Get all component",
                "time_cycle_manual": 10,
                "sequence": 10,
            }
        )

        mrp_routing_workcenter_1 = self.env["mrp.routing.workcenter"].create(
            {
                "routing_id": final_routing.id,
                "workcenter_id": workcenter2.id,
                "name": "Assembly",
                "time_cycle_manual": 60,
                "sequence": 20,
            }
        )

        final_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": final_finished_1.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": final_comp_2.id,
                            "product_qty": 50,
                            "product_uom_id": uom_unit.id,
                            "operation_id": mrp_routing_workcenter_0.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": final_comp_1.id,
                            "product_qty": 1,
                            "product_uom_id": uom_unit.id,
                            "operation_id": mrp_routing_workcenter_0.id,
                        },
                    ),
                ],
                "routing_id": final_routing.id,
            }
        )

        _ = self.env["quality.point"].create(
            {
                "title": "Quality1",
                "product_ids": [(4, final_finished_1.id)],
                "picking_type_ids": [(4, self.env.ref("stock.warehouse0").manu_type_id.id)],
                "operation_id": mrp_routing_workcenter_0.id,
                "test_type_id": self.env.ref("mrp_workorder.test_type_register_consumed_materials").id,
                "component_id": final_comp_2.id,
            }
        )

        _ = self.env["quality.point"].create(
            {
                "title": "Degree saber",
                "product_ids": [(4, final_finished_1.id)],
                "picking_type_ids": [(4, self.env.ref("stock.warehouse0").manu_type_id.id)],
                "operation_id": mrp_routing_workcenter_1.id,
                "test_type_id": self.env.ref("quality_control.test_type_measure").id,
                "note": "Please measure the angle formed by the two adjacent wooden panels",
                "norm": 90,
                "norm_unit": "degrees",
                "tolerance_max": 92,
                "tolerance_min": 88,
                "worksheet": "scroll",
                "worksheet_page": 3,
                "failure_message": "The test has failed: the measure should be between 88 and 92 degrees",
            }
        )

        nb_qty = 5
        serials_final_finished_1 = []
        serials_final_comp_1 = []
        for i in range(nb_qty):
            serials_final_finished_1.append(
                {
                    "product_id": final_finished_1.id,
                    "name": "final_finished_1_%s" % i,
                    "company_id": self.env.company.id,
                }
            )
            serials_final_comp_1.append(
                {"product_id": final_comp_1.id, "name": "final_comp_1_%s" % i, "company_id": self.env.company.id}
            )
        serials_final_finished_1 = self.env["stock.production.lot"].create(serials_final_finished_1)
        serials_final_comp_1 = self.env["stock.production.lot"].create(serials_final_comp_1)
        final_order = Form(self.env["mrp.production"])
        final_order.product_id = final_finished_1
        final_order.bom_id = final_bom
        final_order.product_qty = nb_qty
        final_order = final_order.save()
        final_order.action_confirm()
        final_order.button_plan()

        self.assertEqual(len(final_order.workorder_ids), 2)
        self.assertEqual(final_order.workorder_ids.mapped("duration_expected"), [10 * nb_qty, 60 * nb_qty])

        wo_op_1 = final_order.workorder_ids.sorted()[0]
        wo_op_2 = final_order.workorder_ids.sorted()[1]
        wo_op_1.button_start()
        for i in range(nb_qty):
            wo_form = Form(wo_op_1, view="mrp_workorder.mrp_workorder_view_form_tablet")
            self.assertEqual(wo_form.component_id, final_comp_2, "The suggested component is wrong")
            self.assertEqual(wo_form.qty_done, 50, "The suggested component qty_done is wrong")
            wo = wo_form.save()
            wo.action_next()
            wo_form = Form(wo, view="mrp_workorder.mrp_workorder_view_form_tablet")
            self.assertEqual(wo_form.qty_done, 1, "The suggested component qty_done is wrong")
            wo_form.lot_id = serials_final_comp_1[i]
            wo = wo_form.save()
            wo.action_next()
            wo_form = Form(wo, view="mrp_workorder.mrp_workorder_view_form_tablet")
            wo_form.finished_lot_id = serials_final_finished_1[i]
            wo = wo_form.save()
            if nb_qty - 1 == i:
                wo.do_finish()
            else:
                wo.record_production()

        wo_op_2.button_start()
        for i in range(nb_qty):
            wo_form = Form(wo_op_2, view="mrp_workorder.mrp_workorder_view_form_tablet")
            wo_form.measure = 91
            wo = wo_form.save()
            wo.do_measure()
            if nb_qty - 1 == i:
                wo.do_finish()
            else:
                wo.record_production()

        final_order.button_mark_done()
        self.assertEqual(final_order.state, "done", 'Final state of the MO should be "done"')
        self.assertEqual(final_order.qty_produced, nb_qty)
        self.assertEqual(len(final_order.workorder_ids.check_ids.point_id), 2)

        final_order = {
            "id": final_order.id,
            "lots_produced": serials_final_finished_1.ids,
            "lots_component": serials_final_comp_1.ids,
            "total_durations_workorder": sum(final_order.workorder_ids.mapped("duration")),
            "total_quality_check": len(final_order.workorder_ids.check_ids.point_id),
        }
        return {"final_order": final_order}

    def check(self, init):
        if not init:  # Bypass the check if not init
            return
        final_order = self.env["mrp.production"].browse(init["final_order"]["id"])
        self.assertEqual(
            set(final_order.procurement_group_id.mrp_production_ids.lot_producing_id.ids),
            set(init["final_order"]["lots_produced"]),
        )
        for i in range(len(init["final_order"]["lots_produced"])):
            lot_produce_id, lot_component_id = (
                init["final_order"]["lots_produced"][i],
                init["final_order"]["lots_component"][i],
            )
            backorder = final_order.procurement_group_id.mrp_production_ids.filtered(
                lambda mo: mo.lot_producing_id.id == lot_produce_id
            )
            self.assertEqual(backorder.move_raw_ids.move_line_ids.lot_id.id, lot_component_id)
            self.assertEqual(final_order.move_raw_ids.mapped("product_qty"), [50, 1])

        self.assertEqual(
            len(final_order.procurement_group_id.mrp_production_ids.workorder_ids.check_ids.point_id),
            init["final_order"]["total_quality_check"],
        )
        self.assertEqual(
            sum(final_order.procurement_group_id.mrp_production_ids.workorder_ids.mapped("duration")),
            init["final_order"]["total_durations_workorder"],
        )


@tagged("mrp_v14")
@change_version("saas~13.4")
class TestRoutingQuality(UpgradeCase):
    def prepare(self):
        if release.series != "13.3":
            return {}
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_category_all = self.env.ref("product.product_category_all")
        bom1finished1 = self.env["product.product"].create(
            {"name": "prod_bom_routing", "type": "product", "categ_id": product_category_all.id}
        )
        bom1comp1 = self.env["product.product"].create(
            {"name": "bom1comp1", "type": "product", "categ_id": product_category_all.id}
        )
        workcenter = self.env["mrp.workcenter"].create({"name": "Workcenter"})
        routing1 = self.env["mrp.routing"].create({"name": "Primary Assembly"})
        mrp_routing_workcenter_0 = self.env["mrp.routing.workcenter"].create(
            {
                "routing_id": routing1.id,
                "workcenter_id": workcenter.id,
                "name": "Ope_name_routing1",
                "time_cycle": 60,
                "sequence": 10,
            }
        )
        routing1_bom1 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom1finished1.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom1comp1.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                ],
                "routing_id": routing1.id,
            }
        )
        routing1_bom2 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom1finished1.product_tmpl_id.id,
                "product_qty": 2,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom1comp1.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                ],
                "routing_id": routing1.id,
            }
        )
        qual1 = self.env["quality.point"].create(
            {
                "title": "Quality1",
                "product_ids": [(4, bom1finished1.id)],
                "picking_type_ids": [(4, self.env.ref("stock.warehouse0").manu_type_id.id)],
                "operation_id": mrp_routing_workcenter_0.id,
                "test_type_id": self.env.ref("mrp_workorder.test_type_register_consumed_materials").id,
                "component_id": bom1comp1.id,
            }
        )
        qual2 = self.env["quality.point"].create(
            {
                "title": "Quality2",
                "product_id": [(4, bom1finished1.id)],
                "picking_type_id": [(4, self.env.ref("stock.warehouse0").manu_type_id.id)],
                "operation_id": mrp_routing_workcenter_0.id,
                "test_type_id": self.env.ref("mrp_workorder.test_type_register_consumed_materials").id,
                "component_id": bom1comp1.id,
            }
        )

        order = Form(self.env["mrp.production"])
        order.product_id = bom1finished1
        order.bom_id = routing1_bom1
        order.product_qty = 2
        order = order.save()
        order.action_confirm()
        order.button_plan()
        self.assertEqual(len(order.workorder_ids.check_ids.point_id), 2)
        self.assertEqual(set(order.workorder_ids.check_ids.point_id.ids), {qual1.id, qual2.id})
        self.assertEqual(set(order.workorder_ids.check_ids.point_id.mapped("title")), {"Quality1", "Quality2"})

        return {
            "routing1": {
                "product_id": bom1finished1.id,
                "mo_id": order.id,
                "bom_ids": [routing1_bom1.id, routing1_bom2.id],
                "bom_line_operation_name": mrp_routing_workcenter_0.name,
            }
        }

    def check(self, init):
        if not init:  # Bypass the check if not init
            return
        routing1 = init["routing1"]
        boms = self.env["mrp.bom"].browse(routing1["bom_ids"])
        product = self.env["product.product"].browse(routing1["product_id"])
        self.assertEqual(len(boms.operation_ids), 2)
        self.assertEqual(boms.operation_ids.mapped("name"), [routing1["bom_line_operation_name"]] * 2)
        self.assertEqual(len(boms.operation_ids.quality_point_ids), 4)
        self.assertEqual(len(boms[0].operation_ids.quality_point_ids), 2)
        self.assertEqual(len(boms[1].operation_ids.quality_point_ids), 2)
        self.assertEqual(boms[0].operation_ids.quality_point_ids.product_ids, product)
        self.assertEqual(boms[1].operation_ids.quality_point_ids.product_ids, product)

        order = self.env["mrp.production"].browse(routing1["mo_id"])
        self.assertEqual(len(order.workorder_ids.check_ids.point_id), 2)
        self.assertEqual(
            order.workorder_ids.check_ids.point_id[0].picking_type_ids.id,
            self.env.ref("stock.warehouse0").manu_type_id.id,
        )
        self.assertEqual(len(order.workorder_ids.check_ids.point_id.product_ids), 1)
        self.assertEqual(order.workorder_ids.check_ids.point_id.product_ids, product)
        self.assertEqual(order.workorder_ids.check_ids.point_id.product_ids[0].product_tmpl_id, boms[0].product_tmpl_id)
        self.assertEqual(set(order.workorder_ids.check_ids.point_id.mapped("title")), {"Quality1", "Quality2"})
