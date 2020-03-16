# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'crm_lead2opportunity_partner', 'lead_id', 'int4')
    util.create_column(cr, 'crm_lead2opportunity_partner_mass', 'lead_id', 'int4')
    util.remove_model(cr, 'crm.partner.binding')

    cr.execute('ALTER TABLE "crm_lead_tag_rel" RENAME TO "crm_tag_rel"')
