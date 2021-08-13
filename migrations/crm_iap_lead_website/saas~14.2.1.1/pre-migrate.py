# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    module = "website_crm_iap_reveal" if util.version_gte("saas~14.5") else "crm_iap_lead_website"
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("%s.access_crm_reveal_rule{,_manager}" % module))
    util.rename_xmlid(cr, *eb("%s.access_crm_reveal_view{,_manager}" % module))
