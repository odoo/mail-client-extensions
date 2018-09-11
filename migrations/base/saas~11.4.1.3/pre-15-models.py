# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE res_partner
           SET active = true
         WHERE active = false
           AND id IN (SELECT partner_id FROM res_users WHERE active=true)
    """)

    # remove settings fields (added by other modules, but regroup them here)
    for mod in "sale_expense sale_timesheet mrp_maintenance repair hr_timesheet".split():
        util.remove_field(cr, "res.config.settings", "module_" + mod)
