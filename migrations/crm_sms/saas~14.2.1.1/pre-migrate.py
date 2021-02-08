# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "crm_sms.crm_lead_view_list_activities", "crm_sms.crm_case_tree_view_oppor", noupdate=False)
