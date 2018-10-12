# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for view in {"aged_payable", "partner_ledget", "general_ledger"}:
        util.remove_view(cr, "account_reports.template_{}_report".format(view))

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("account_reports.template_coa_{report,table_header}"))
