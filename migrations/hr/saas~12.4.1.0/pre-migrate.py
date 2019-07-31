# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "hr_plan_activity_type"):
        # model introduced in saas-12.2
        # name was a related, and is now a simple varchar field called summary...
        util.create_column(cr, "hr_plan_activity_type", "name", "varchar")
        cr.execute(
            """
            UPDATE hr_plan_activity_type p
               SET name = t.name
              FROM mail_activity_type t
             WHERE t.id = p.activity_type_id
            """
        )
        util.rename_field(cr, "hr.plan.activity.type", "name", "summary")

    if util.table_exists(cr, "hr_departure_wizard"):
        # model introduced in saas-12.2
        util.create_column(cr, "hr_departure_wizard", "employee_id", "int4")
