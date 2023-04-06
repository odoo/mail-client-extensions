# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mailing.mailing", "crm_lead_activated", "use_leads")
    util.update_field_usage(cr, "mailing.mailing", "crm_opportunities_count", "crm_lead_count")
    util.remove_field(cr, "mailing.mailing", "crm_opportunities_count")
