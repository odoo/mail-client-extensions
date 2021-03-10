# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "crm_iap_lead_mining_request", "error_type", "varchar")
    cr.execute(
        """
        UPDATE crm_iap_lead_mining_request
           SET error_type = 'credits'
         WHERE state = 'error'
        """
    )
    util.remove_field(cr, "crm.iap.lead.mining.request", "error")
