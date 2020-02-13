# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.new_module_dep(cr, "crm_iap_lead", "partner_autocomplete")
    util.new_module_dep(cr, "crm_iap_lead_enrich", "partner_autocomplete")
    util.remove_module(cr, "odoo_referral_portal")
