# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "crm.iap.lead.mining.request", "leads_count", "lead_count")

    util.remove_view(cr, "crm_iap_lead.lead_message_template")
