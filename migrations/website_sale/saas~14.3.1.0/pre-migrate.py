# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_ui_view
           SET active = TRUE,
               customize_show = FALSE
         WHERE key = 'website_sale.ecom_show_extra_fields'
    """)
