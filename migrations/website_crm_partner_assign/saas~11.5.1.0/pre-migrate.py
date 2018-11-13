# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record_if_unchanged(cr, "website_crm_partner_assign.email_template_lead_forward_mail")
    util.remove_model(cr, "crm.lead.report.assign")
