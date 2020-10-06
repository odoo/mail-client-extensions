# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "crm.lead", "reveal_id", "crm_iap_lead", "iap_crm")
    util.move_field_to_module(cr, "crm.lead", "reveal_id", "crm_iap_lead_enrich", "iap_crm")
