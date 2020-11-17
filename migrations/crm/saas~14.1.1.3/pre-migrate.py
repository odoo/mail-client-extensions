# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "crm.email_template_opportunity_mail")
    util.remove_record(cr, "crm.crm_lead_act_window_compose")
