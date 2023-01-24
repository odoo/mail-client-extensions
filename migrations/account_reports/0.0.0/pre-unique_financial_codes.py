# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("16.0"):
        return

    cr.execute(
        """
            SELECT name
              FROM ir_model_data
             WHERE model = 'account.financial.html.report.line'
               AND module = 'account_reports'
               AND noupdate = false
        """
    )

    for name in cr.fetchall():
        xmlid = "account_reports." + name[0]
        if util.is_changed(cr, xmlid):
            util.force_noupdate(cr, xmlid)
