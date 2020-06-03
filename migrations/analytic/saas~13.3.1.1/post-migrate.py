# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.check_company_consistency(cr, "account.analytic.account", "group_id")
    util.check_company_consistency(cr, "account.analytic.account", "partner_id")
    util.check_company_consistency(cr, "account.analytic.line", "account_id")
    util.check_company_consistency(cr, "account.analytic.line", "partner_id")
    util.check_company_consistency(cr, "account.analytic.line", "tag_ids")
