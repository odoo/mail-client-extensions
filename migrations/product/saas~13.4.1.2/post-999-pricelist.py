# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE product_pricelist_item
                     SET date_end = date_end + interval '23 hours 59 minutes 59 seconds'
                   WHERE date_end is not null
               """)
