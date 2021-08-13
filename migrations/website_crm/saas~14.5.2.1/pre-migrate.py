# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "website_crm.website_visitor_crm_lead_action", "website_crm.crm_lead_action_from_visitor")
