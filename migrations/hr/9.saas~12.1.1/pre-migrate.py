# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.ref(cr, "hr.employee"):
        util.rename_xmlid(cr, *eb("hr.employee{,_root}"))
    elif util.ref(cr, "hr.employee_fp"):
        util.rename_xmlid(cr, *eb("hr.employee_{fp,root}"))
    else:
        # Try to match an existing one
        cr.execute(
            """
            INSERT INTO ir_model_data("module", name, model, res_id, noupdate)
                 SELECT 'hr', 'employee_root', 'hr.employee', e.id, TRUE
                   FROM hr_employee e
                   JOIN resource_resource r ON r.id = e.resource_id
                  WHERE r.user_id = %s
               ORDER BY r.active, e.id
                  LIMIT 1
        """,
            [util.ref(cr, "base.user_root")],
        )
