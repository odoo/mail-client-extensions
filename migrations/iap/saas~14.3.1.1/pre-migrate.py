# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "iap.enrich.api", "crm_iap_lead_enrich", "iap")
