# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("crm_iap_lead_website.access_crm_reveal_rule{,_manager}"))
    util.rename_xmlid(cr, *eb("crm_iap_lead_website.access_crm_reveal_view{,_manager}"))
