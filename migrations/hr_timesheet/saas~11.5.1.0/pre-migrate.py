# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "analytic_account_id")
    util.move_field_to_module(cr, "res.company", "project_time_mode_id", "project", "hr_timesheet")
    util.create_column(cr, "res_company", "timesheet_encode_uom_id", "integer")

    hour = util.ref(cr, "uom.product_uom_hour")
    if not hour:
        cr.execute("""
            SELECT id
              FROM uom_uom
             WHERE measure_type = 'time'
          ORDER BY uom_type = 'reference' DESC, id
             LIMIT 1
        """)
        [hour] = cr.fetchone() or [None]

    cr.execute("UPDATE res_company SET timesheet_encode_uom_id=%s", [hour])

    util.create_column(cr, "uom_uom", "timesheet_widget", "varchar")
