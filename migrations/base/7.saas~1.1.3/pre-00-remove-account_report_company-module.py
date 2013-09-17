# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    """In 7.0, the module "account_report_company" was a temporary module and
       its functionnality is now part of the "base" and "account" modules.
    """

    MODULE = 'account_report_company'

    # reassign fields
    cr.execute("""
        UPDATE ir_model_data
           SET module=%s
         WHERE module=%s
           AND name=%s
    """, ('base', MODULE, 'field_res_partner_display_name'))

    cr.execute("""
        UPDATE ir_model_data
           SET module=%s
         WHERE module=%s
           AND name IN %s
    """, ('account', MODULE, ('field_account_invoice_commercial_partner_id',
                              'field_account_invoice_report_commercial_partner_id')))

    util.remove_module(cr, MODULE)
