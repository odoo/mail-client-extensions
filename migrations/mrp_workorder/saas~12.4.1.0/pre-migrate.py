# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "mrp.workorder", "move_line_id", "workorder_line_id")
    util.rename_field(cr, "quality.check", "move_line_id", "workorder_line_id")
    util.rename_field(cr, "quality.check", "final_lot_id", "finished_lot_id")

    util.remove_view(cr, "mrp_workorder.mrp_routing_workcenter_view_form_inherit_workorder")

    util.create_column(cr, "res_config_settings", "group_mrp_wo_tablet_timer", "boolean")

    cr.execute("""
        WITH timer_group AS (
            INSERT INTO res_groups (name, category_id)
                VALUES ('Manage Work Order timer on Tablet View', %s)
            RETURNING id
        )
        INSERT INTO ir_model_data (model, res_id, name, module)
        VALUES ('res.groups', (select id from timer_group), 'group_mrp_wo_tablet_timer', 'mrp_workorder')
    """ % util.ref(cr, 'base.module_category_hidden'))
