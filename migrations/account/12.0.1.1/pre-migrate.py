# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    # moved with odoo/odoo@49eb24a46771792bec454f6c4693c19d2b5b05b6
    util.rename_xmlid(cr, *eb("{sale_timesheet,account}.account_analytic_line_rule_billing_user"))
