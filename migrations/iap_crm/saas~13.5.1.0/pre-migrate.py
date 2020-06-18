# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "crm_iap_lead"):
        util.move_field_to_module(cr, "crm.lead", "reveal_id",
                                  "crm_iap_lead", "iap_crm")
    elif util.module_installed(cr, "crm_iap_lead_enrich"):
        util.move_field_to_module(cr, "crm.lead", "reveal_id",
                                  "crm_iap_lead_enrich", "iap_crm")
