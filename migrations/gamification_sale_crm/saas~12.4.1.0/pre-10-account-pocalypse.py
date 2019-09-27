# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Manual update due to noupdate block.
    util.force_noupdate(cr, 'gamification_sale_crm.definition_crm_tot_invoices', noupdate=False)
    util.force_noupdate(cr, 'gamification_sale_crm.definition_crm_nbr_paid_sale_order', noupdate=False)
    util.force_noupdate(cr, 'gamification_sale_crm.definition_crm_tot_paid_sale_order', noupdate=False)
    util.force_noupdate(cr, 'gamification_sale_crm.definition_crm_nbr_customer_refunds', noupdate=False)
    util.force_noupdate(cr, 'gamification_sale_crm.definition_crm_tot_customer_refunds', noupdate=False)
