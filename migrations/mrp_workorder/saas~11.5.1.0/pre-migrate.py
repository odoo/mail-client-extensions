# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    ttid = util.rename_xmlid(cr, "quality_mrp_workorder.test_type_dummy", "mrp_workorder.test_type_text")
    if ttid:
        # manual update
        cr.execute("UPDATE quality_point_test_type SET name = 'Text', technical_name = 'text' WHERE id = %s", [ttid])
        cr.execute("DELETE FROM ir_translation WHERE name = 'quality.point.test_type,name' AND res_id = %s", [ttid])

    util.rename_xmlid(cr, *eb("{quality_,}mrp_workorder.test_picture"))

    util.move_field_to_module(cr, "mrp.production.workcenter.line", "picture", "quality_mrp_workorder", "mrp_workorder")

    util.remove_record(cr, "mrp_workorder.menu_mrp_production_plan")
    util.remove_record(cr, "mrp_workorder.menu_mrp_production_pending")
    util.remove_record(cr, "mrp_workorder.mrp_production_menu_planning")
