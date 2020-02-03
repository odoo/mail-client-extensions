# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.setup_overdue_msg_view_company_form")
    util.remove_view(cr, "account_reports.customer_statements_form_view")
    util.remove_view(cr, "account_reports.customer_statements_tree_view")
    util.remove_view(cr, "account_reports.customer_statements_search_view")
    util.remove_record(cr, "account_reports.action_view_list_customer_statements")
    util.remove_menus(cr, [util.ref(cr, "account_reports.customer_statements_menu")])
    util.remove_record(cr, "account_reports.res_partner_view_form")
    util.remove_record(cr, "account_reports.action_account_reports_customer_statements_do_followup")
