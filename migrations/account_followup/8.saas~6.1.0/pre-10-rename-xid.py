# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    module = "account_reports_followup" if util.version_gte("9.0") else "account_followup"
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb(module + ".view_account_followup_stat_{graph,pivot}"))
