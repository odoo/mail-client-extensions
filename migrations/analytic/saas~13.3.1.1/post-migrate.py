# -*- coding: utf-8 -*-
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    inconsistencies.verify_companies(cr, "account.analytic.account", "group_id")
    inconsistencies.verify_companies(cr, "account.analytic.account", "partner_id")
    inconsistencies.verify_companies(cr, "account.analytic.line", "account_id")
    inconsistencies.verify_companies(cr, "account.analytic.line", "partner_id")
    inconsistencies.verify_companies(cr, "account.analytic.line", "tag_ids")
