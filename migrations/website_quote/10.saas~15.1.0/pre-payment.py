# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_transaction
           SET callback_model_id = (SELECT id FROM ir_model WHERE model='sale.order'),
               callback_res_id = sale_order_id,
               callback_method = '_confirm_online_quote'
        WHERE callback_eval = 'self.sale_order_id._confirm_online_quote(self)'
    """)
