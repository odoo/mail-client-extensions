# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sale_crm.account_invoice_groupby_inherit',
                              'sale.account_invoice_groupby_inherit')
    util.rename_xmlid(cr, 'sale_crm.mt_salesteam_order_sent', 'sale.mt_salesteam_order_sent')
    util.rename_xmlid(cr, 'sale_crm.mt_salesteam_order_confirmed', 'sale.mt_salesteam_order_confirmed')

    # Set correct sequnce id for 'Quotation Send' and 'Sales Order Confirmed'
    cr.execute("""
        UPDATE mail_message_subtype
        SET sequence =
                (CASE
                    WHEN name='Quotation Send'
                    THEN 20
                    WHEN name='Sales Order Confirmed'
                    THEN 21
                ELSE sequence
                END)
        WHERE res_model='crm.case.section'
        """)
