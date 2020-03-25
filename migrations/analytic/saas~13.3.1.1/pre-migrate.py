# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # ===========================================================
    # Account Security (PR:46586 & 8986)
    # ===========================================================

    util.check_company_fields(cr, 'account.analytic.account', 'group_id')
    util.check_company_fields(cr, 'account.analytic.account', 'partner_id')
    util.check_company_fields(cr, 'account.analytic.line', 'account_id')
    util.check_company_fields(cr, 'account.analytic.line', 'partner_id')
    util.check_company_fields(cr, 'account.analytic.line', 'tag_ids')
