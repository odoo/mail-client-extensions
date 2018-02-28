# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE payment_transaction SET callback_method=NULL where callback_method='_confirm_online_quote'")
