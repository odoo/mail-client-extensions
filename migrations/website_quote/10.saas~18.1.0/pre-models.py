# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE sale_order SET require_payment=1 WHERE require_payment=2")
    cr.execute("UPDATE sale_quote_template SET require_payment=1 WHERE require_payment=2")
