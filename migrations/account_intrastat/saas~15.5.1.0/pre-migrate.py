# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.intrastat.report")
    util.remove_view(cr, "account_intrastat.search_template")
    util.remove_view(cr, "account_intrastat.view_intrastat_code_expiry_search")
    util.remove_view(cr, "account_intrastat.view_report_intrastat_code_expiry_tree")
    util.remove_view(cr, "account_intrastat.view_report_intrastat_code_expiry_form")
    util.remove_view(cr, "account_intrastat.invoice_form_inherit_account_intrastat_expiry")
    util.remove_view(cr, "account_intrastat.account_intrastat_expiry_product_template_search_view")
    util.rename_xmlid(
        cr,
        "account_intrastat.product_product_tree_view_account_intrastat_expiry",
        "account_intrastat.product_product_tree_view_account_intrastat",
    )
    util.rename_xmlid(
        cr,
        "account_intrastat.account_intrastat_expiry_product_category_search_view",
        "account_intrastat.account_intrastat_product_category_search_view",
    )
    util.rename_xmlid(
        cr,
        "account_intrastat.product_category_tree_view_account_intrastat_expiry",
        "account_intrastat.product_category_tree_view_account_intrastat",
    )
    util.rename_xmlid(
        cr,
        "account_intrastat.account_intrastat_expiry_main_template",
        "account_intrastat.account_intrastat_main_template",
    )
