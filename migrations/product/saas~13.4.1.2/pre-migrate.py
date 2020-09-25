# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            ALTER TABLE product_pricelist_item
            ALTER COLUMN date_start TYPE timestamp,
            ALTER COLUMN date_end TYPE timestamp USING date_end + interval '23 hours 59 minutes 59 seconds'
        """
    )
