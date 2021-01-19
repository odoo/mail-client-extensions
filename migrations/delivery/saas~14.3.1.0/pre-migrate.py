# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='product.volume_in_cubic_feet'")
    value = cr.fetchone()
    if value != 1:
        cr.execute(
            """
            UPDATE product_packaging p
                SET height = p.height * 1000,
                    width = p.width * 1000,
                    packaging_length = p.packaging_length * 1000
            """
        )
