# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "crm.iap.lead.mining.request", "technology_ids")
    util.remove_model(cr, "crm.iap.lead.technology")
    util.remove_field(cr, "crm.iap.lead.mining.request", "lead_number_info")
    util.remove_field(cr, "crm.iap.lead.mining.request", "lead_total_credit")
    util.remove_field(cr, "crm.iap.lead.mining.request", "contact_credit_per_company")
    util.remove_field(cr, "crm.iap.lead.mining.request", "contact_total_credit")
