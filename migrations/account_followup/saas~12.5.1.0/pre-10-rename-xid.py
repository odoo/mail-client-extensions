# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "account_followup.res_config_settings_view_form")

    util.rename_xmlid(cr, *eb("account_{reports,followup}.action_report_followup"))
    util.rename_xmlid(cr, *eb("account_{reports,followup}.report_followup_print_all"))
    util.rename_xmlid(cr, *eb("account_{reports,followup}.property_account_payment_next_action_date"))
    util.rename_xmlid(cr, *eb("account_{reports,followup}.followup_filter_info_template"))
    util.rename_xmlid(cr, *eb("account_{reports,followup}.line_template_followup_report"))
    util.rename_xmlid(cr, *eb("account_{reports,followup}.followup_search_template"))
