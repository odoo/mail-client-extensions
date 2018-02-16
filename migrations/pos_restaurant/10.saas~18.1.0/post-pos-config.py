# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE pos_config c
           SET module_pos_restaurant = (
                            iface_printbill = true
                         OR iface_splitbill = true
                         OR tip_product_id IS NOT NULL
                         OR iface_orderline_notes = true
                         OR EXISTS(SELECT 1 FROM restaurant_floor WHERE pos_config_id = c.id)
                         OR EXISTS(SELECT 1 FROM pos_config_printer_rel WHERE config_id = c.id)
               ),
               is_table_management = EXISTS(SELECT 1 FROM restaurant_floor WHERE pos_config_id = c.id),
               is_order_printer = EXISTS(SELECT 1 FROM pos_config_printer_rel WHERE config_id = c.id)
    """)
