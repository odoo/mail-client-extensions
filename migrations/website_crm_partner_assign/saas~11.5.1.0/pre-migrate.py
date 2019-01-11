# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_crm_partner_assign.email_template_lead_forward_mail", util.update_record_from_xml)
    util.remove_model(cr, "crm.lead.report.assign")
