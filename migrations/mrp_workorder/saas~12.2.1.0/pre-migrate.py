# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "date_planned_start_wo")
    util.remove_field(cr, "mrp.production", "date_planned_finished_wo")
    util.rename_field(cr, "quality.check", "lot_id", "final_lot_id")

    util.remove_view(cr, "mrp_workorder.mrp_production_view_form_inherit_planning")
