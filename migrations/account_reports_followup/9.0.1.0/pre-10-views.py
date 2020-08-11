# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="account_reports_followup.customer_followup_tree")
    util.remove_view(cr, xml_id="account_reports_followup.view_partner_inherit_customer_followup_tree")
    util.remove_view(cr, xml_id="account_reports_followup.customer_followup_search_view")
    util.remove_view(cr, xml_id="account_reports_followup.view_partner_inherit_followup_form")
