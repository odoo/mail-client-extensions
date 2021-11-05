# -*- coding: utf-8 -*-

from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@tagged("mrp_v14")
@change_version("13.4")
class TestMrpPLM(UpgradeCase):
    def prepare(self):
        group_user = self.env.ref("base.group_user")
        group_user.write({"implied_ids": [(4, self.env.ref("mrp.group_mrp_routings").id)]})
        self.assertTrue(self.env.user.has_group("mrp.group_mrp_routings"))
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_category_all = self.env.ref("product.product_category_all")

        workcenter1 = self.env["mrp.workcenter"].create({"name": "Mine"})
        workcenter2 = self.env["mrp.workcenter"].create({"name": "Craft Table"})

        bom_routing = self.env["mrp.routing"].create(
            {
                "name": "Fanta Tuto",
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "workcenter_id": workcenter2.id,
                            "name": "Get all component",
                            "time_cycle_manual": 60,
                            "sequence": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "workcenter_id": workcenter2.id,
                            "name": "Craft it Dude!!",
                            "time_cycle_manual": 30,
                            "sequence": 20,
                        },
                    ),
                ],
            }
        )

        bom_pro_finished_1 = self.env["product.product"].create(
            {"name": "Diamond Sword", "type": "product", "categ_id": product_category_all.id}
        )
        bom_pro_finished_2 = self.env["product.product"].create(
            {"name": "Diamond Pickaxe", "type": "product", "categ_id": product_category_all.id}
        )
        bom_pro_finished_3 = self.env["product.product"].create(
            {"name": "Stone Shovel", "type": "product", "categ_id": product_category_all.id}
        )
        bom_pro_comp_1 = self.env["product.product"].create(
            {"name": "Wood Stick", "type": "product", "categ_id": product_category_all.id}
        )
        bom_pro_comp_2 = self.env["product.product"].create(
            {"name": "Diamond", "type": "product", "categ_id": product_category_all.id}
        )
        bom_pro_comp_3 = self.env["product.product"].create(
            {"name": "Stone", "type": "product", "categ_id": product_category_all.id}
        )

        bom1 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom_pro_finished_1.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom_pro_comp_1.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": bom_pro_comp_2.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                ],
                "routing_id": bom_routing.id,
            }
        )
        bom2 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom_pro_finished_2.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom_pro_comp_1.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": bom_pro_comp_2.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                ],
                "routing_id": bom_routing.id,
            }
        )
        bom3 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom_pro_finished_3.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": bom_pro_comp_1.id, "product_qty": 2, "product_uom_id": uom_unit.id}),
                    (0, 0, {"product_id": bom_pro_comp_2.id, "product_qty": 1, "product_uom_id": uom_unit.id}),
                ],
                "routing_id": bom_routing.id,
            }
        )

        # For a finished routing ECO
        # The historic should be correct for the bom1 and bom2
        type_id = self.env["mrp.eco.type"].search([], limit=1).id
        eco_to_finished = self.env["mrp.eco"].create(
            {
                "name": "1. Fixes times and workcenter of routing",
                "type_id": type_id,
                "stage_id": self.env["mrp.eco.stage"].search([("type_id", "=", type_id)], limit=1).id,
                "note": "Change",
                "type": "routing",
                "routing_id": bom_routing.id,
            }
        )
        eco_to_finished.action_new_revision()
        operations = eco_to_finished.new_routing_id.operation_ids
        operations[0].workcenter_id = workcenter1.id
        operations[1].time_cycle_manual = 5
        stage_apply = self.env["mrp.eco.stage"].search(
            [("type_id", "=", type_id), ("allow_apply_change", "=", True)], limit=1
        )
        eco_to_finished.stage_id = stage_apply.id
        eco_to_finished.action_apply()
        # Change the routing in the BoM
        bom1.routing_id = eco_to_finished.new_routing_id
        bom2.routing_id = eco_to_finished.new_routing_id

        # reactivate the bom for the first eco confirmed
        bom_routing.active = True
        # For a confirmed eco where the bom is the same than the routing
        eco_confirmed_1 = self.env["mrp.eco"].create(
            {
                "name": "2. Correct product use",
                "type_id": type_id,
                "stage_id": self.env["mrp.eco.stage"].search([("type_id", "=", type_id)], limit=1).id,
                "note": "Bla bla bla",
                "type": "both",
                "product_tmpl_id": bom3.product_tmpl_id.id,
                "bom_id": bom3.id,
                "routing_id": bom_routing.id,
            }
        )
        eco_confirmed_1.action_new_revision()
        eco_confirmed_1.new_bom_id.bom_line_ids.filtered(
            lambda l: l.product_id == bom_pro_comp_2
        ).product_id = bom_pro_comp_3
        eco_confirmed_1.new_routing_id.operation_ids[0].time_cycle_manual = 5
        eco_confirmed_1.new_routing_id.operation_ids[1].time_cycle_manual = 2

        # For a Confirmed 'both' on routing linked to bom1 and bom2
        eco_confirmed_2 = self.env["mrp.eco"].create(
            {
                "name": "3. Fixes quantities and tune time",
                "type_id": type_id,
                "stage_id": self.env["mrp.eco.stage"].search([("type_id", "=", type_id)], limit=1).id,
                "note": "Bla bla bla",
                "type": "both",
                "product_tmpl_id": bom2.product_tmpl_id.id,
                "bom_id": bom2.id,
                "routing_id": eco_to_finished.new_routing_id.id,
            }
        )
        eco_confirmed_2.action_new_revision()
        eco_confirmed_2.new_bom_id.bom_line_ids.filtered(lambda l: l.product_id == bom_pro_comp_2).product_qty = 3
        eco_confirmed_2.new_routing_id.operation_ids[0].time_cycle_manual = 45

        # For a Confirmed 'routing' on routing linked to bom1 and bom2 => 2 ECO with two BoM
        eco_confirmed_3 = self.env["mrp.eco"].create(
            {
                "name": "4. ARM et WHE, des tyrans!",
                "note": "One day, I asked to clean everything in stock module and they refuse...",
                "type_id": type_id,
                "stage_id": self.env["mrp.eco.stage"].search([("type_id", "=", type_id)], limit=1).id,
                "type": "routing",
                "routing_id": eco_to_finished.new_routing_id.id,
            }
        )
        eco_confirmed_3.action_new_revision()
        eco_confirmed_3.new_routing_id.operation_ids[0].time_cycle_manual = 10

        # For a Draft routing ECO
        # => Should be duplicate for each bom using this routing and nothing else.
        _ = self.env["mrp.eco"].create(
            {
                "name": "5. Don't fix anything",
                "type_id": type_id,
                "stage_id": self.env["mrp.eco.stage"].search([("type_id", "=", type_id)], limit=1).id,
                "note": "Change ",
                "type": "routing",
                "routing_id": eco_to_finished.new_routing_id.id,
            }
        )

        self.assertEqual(bom1.routing_id.operation_ids[0].workcenter_id, workcenter1)
        self.assertEqual(bom2.routing_id.operation_ids[0].workcenter_id, workcenter1)
        self.assertEqual(bom1.routing_id.operation_ids[1].time_cycle_manual, 5)
        self.assertEqual(bom2.routing_id.operation_ids[1].time_cycle_manual, 5)

        return {
            "bom1_id": bom1.id,
            "bom2_id": bom2.id,
            "bom3_id": bom3.id,
            "bom_pro_finished_1": bom_pro_finished_1.id,
            "bom_pro_finished_2": bom_pro_finished_2.id,
            "bom_pro_finished_3": bom_pro_finished_3.id,
            "workcenter1_id": workcenter1.id,
            "workcenter2_id": workcenter2.id,
        }

    def check(self, init):
        if not init:  # Bypass the check if not init
            return

        product_fin_1 = self.env["product.product"].browse(init["bom_pro_finished_1"])
        product_fin_2 = self.env["product.product"].browse(init["bom_pro_finished_2"])
        product_fin_3 = self.env["product.product"].browse(init["bom_pro_finished_3"])
        bom1 = self.env["mrp.bom"].browse(init["bom1_id"])
        bom2 = self.env["mrp.bom"].browse(init["bom2_id"])
        workcenter1 = self.env["mrp.workcenter"].browse(init["workcenter1_id"])
        workcenter2 = self.env["mrp.workcenter"].browse(init["workcenter2_id"])

        # active boms shouldn't change
        self.assertEqual(bom1, self.env["mrp.bom"]._bom_find(product=product_fin_1))
        self.assertEqual(bom2, self.env["mrp.bom"]._bom_find(product=product_fin_2))
        self.assertEqual(bom1.operation_ids[0].workcenter_id, workcenter1)
        self.assertEqual(bom2.operation_ids[0].workcenter_id, workcenter1)
        self.assertEqual(bom1.operation_ids[1].time_cycle_manual, 5)
        self.assertEqual(bom2.operation_ids[1].time_cycle_manual, 5)

        # Check the eco_to_finished
        # It should create old bom version to keep the PLM historic
        eco_finished_bom_1 = self.env["mrp.eco"].search([("new_bom_id", "=", init["bom1_id"])])
        eco_finished_bom_2 = self.env["mrp.eco"].search([("new_bom_id", "=", init["bom2_id"])])
        self.assertEqual(len(eco_finished_bom_1), 1)
        self.assertEqual(len(eco_finished_bom_2), 1)
        self.assertEqual(eco_finished_bom_1.state, "done")
        self.assertEqual(eco_finished_bom_1.type, "bom")
        self.assertEqual(eco_finished_bom_2.state, "done")
        self.assertEqual(eco_finished_bom_2.type, "bom")
        self.assertEqual(eco_finished_bom_1.bom_id.operation_ids[0].workcenter_id, workcenter2)
        self.assertEqual(eco_finished_bom_1.bom_id.operation_ids[1].time_cycle_manual, 30)
        self.assertEqual(eco_finished_bom_2.bom_id.operation_ids[0].workcenter_id, workcenter2)
        self.assertEqual(eco_finished_bom_2.bom_id.operation_ids[1].time_cycle_manual, 30)

        # Check the eco_confirmed_1
        # It just should change the both into bom_id and only have one eco
        bom_eco_confirmed_2 = self.env["mrp.bom"].search(
            [("product_tmpl_id", "=", product_fin_3.product_tmpl_id.id), ("active", "=", True)]
        )
        self.assertEqual(len(bom_eco_confirmed_2), 1)  # Only one active
        new_bom_eco_confirmed_2 = self.env["mrp.bom"].search(
            [("previous_bom_id", "=", bom_eco_confirmed_2.id), ("active", "=", False)]
        )
        self.assertEqual(len(new_bom_eco_confirmed_2), 1)

        bom_eco_confirmed_2 = self.env["mrp.eco"].search([("name", "ilike", "2. Correct product use")])
        self.assertEqual(len(bom_eco_confirmed_2), 1)
        self.assertEqual(bom_eco_confirmed_2.type, "bom")
        self.assertEqual(bom_eco_confirmed_2.product_tmpl_id, product_fin_3.product_tmpl_id)
        self.assertEqual(new_bom_eco_confirmed_2, bom_eco_confirmed_2.new_bom_id)

        # Check the eco_confirmed_2
        # It should change the both eco type into bom type
        eco_confirmed_2 = self.env["mrp.eco"].search(
            [
                ("name", "ilike", "3. Fixes quantities and "),
            ]
        )
        self.assertEqual(len(eco_confirmed_2), 1)  # Only one because both type
        self.assertEqual(eco_confirmed_2.new_bom_id.operation_ids[0].time_cycle_manual, 45)

        # Check the eco_confirmed_3
        # It should change the both eco type into bom type
        ecos_confirmed_3 = self.env["mrp.eco"].search(
            [
                ("name", "ilike", "4. ARM et WHE, des tyrans!"),
            ]
        )
        self.assertEqual(len(ecos_confirmed_3), 2)  # 2 for duplicate bom and 1 for the old bom
        self.assertEqual(ecos_confirmed_3[0].new_bom_id.operation_ids[0].time_cycle_manual, 10)
        self.assertEqual(ecos_confirmed_3[1].new_bom_id.operation_ids[0].time_cycle_manual, 10)

        # Check the eco in Draft
        eco_draft = self.env["mrp.eco"].search(
            [
                ("name", "ilike", "5. Don't fix anything"),
            ]
        )
        self.assertEqual(len(eco_draft), 2)
        self.assertFalse(eco_draft.new_bom_id)
        self.assertEqual(set(eco_draft.bom_id.ids), set((bom1 + bom2).ids))
