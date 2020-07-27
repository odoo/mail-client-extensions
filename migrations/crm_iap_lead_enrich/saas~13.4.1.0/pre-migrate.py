# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "crm_iap_lead_enrich.mail_message_lead_enrich_with_data")
