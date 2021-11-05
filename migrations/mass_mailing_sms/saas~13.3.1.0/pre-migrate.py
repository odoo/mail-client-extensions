# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing_sms.mailing_contact_view_tree_sms")
    for view in "pivot graph search".split():
        util.remove_view(cr, f"mass_mailing_sms.mailing_trace_report_view_{view}")

    util.force_noupdate(cr, "mass_mailing_sms.mailing_contact_view_search", False)
    util.force_noupdate(cr, "mass_mailing_sms.mailing_contact_view_form", False)
    util.force_noupdate(cr, "mass_mailing_sms.mailing_contact_view_kanban", False)
    util.force_noupdate(cr, "mass_mailing_sms.mailing_contact_action_sms", False)
