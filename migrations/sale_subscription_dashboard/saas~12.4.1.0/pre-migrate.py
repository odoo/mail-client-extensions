# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("sale_subscription_dashboard.{invoice,move}_line_entries_report_pivot"))
    util.rename_xmlid(cr, *eb("sale_subscription_dashboard.{invoice,move}_line_entries_report_search"))

