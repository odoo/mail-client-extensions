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
    util.remove_view(cr, "account_reports.qunit_suite")
    util.remove_view(cr, "account_reports.assets_followup_report")

    # move views (and other records)
    eb = util.expand_braces
    moved_views = """
        report_followup_print_all
        followup_filter_info_template
        line_template_followup_report
        template_followup_report
        followup_search_template
    """

    if util.module_installed(cr, "account_followup"):
        util.remove_view(cr, "account_followup.template_followup_report")
        for view in util.splitlines(moved_views):
            util.rename_xmlid(cr, *eb("account_{reports,followup}." + view), noupdate=False)
        util.rename_xmlid(cr, *eb("account_{reports,followup}.action_report_followup"), noupdate=False)
        util.rename_xmlid(cr, *eb("account_{reports,followup}.property_account_payment_next_action_date"))
    else:
        for view in util.splitlines(moved_views):
            util.remove_view(cr, "account_reports." + view)
        util.remove_record(cr, "account_reports.action_report_followup")
        util.force_noupdate(cr, "account_reports.property_account_payment_next_action_date", True)
