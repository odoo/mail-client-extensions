# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE pos_config c
           SET module_pos_discount = (discount_product_id IS NOT NULL)
    """)
