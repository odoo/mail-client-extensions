# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('account{_reports,}.account_reports_legal_statements_menu'))

    # in 10.saas~17, the module `website_account` steal records from `website_portal_sale`.
    # Now that `website_account` has been merged into `account`, we need to do it also.
    if util.parse_version(version) >= util.parse_version("10.saas~17"):
        # from 10.saas~17
        from_module = "account"  # renamed from `website_account`
    else:
        from_module = "sale"  # renamed from `website_portal_sale`

        util.rename_xmlid(cr, *eb("{sale,account}.portal_my_home_menu_invoice"))
        util.rename_xmlid(cr, *eb("{sale,account}.portal_my_home_invoice"))
        util.rename_xmlid(cr, *eb("{sale,account}.portal_my_invoices"))

    # However has some stolen records have now been deleted.
    util.remove_record(cr, from_module + ".portal_account_invoice_user_rule")
    util.remove_record(cr, from_module + ".portal_account_invoice_line_rule")
    util.remove_record(cr, from_module + ".access_account_invoice")
    util.remove_record(cr, from_module + ".access_account_invoice_line")
    util.remove_view(cr, from_module + ".view_account_invoice_filter_share")
