# -*- coding: utf-8 -*-
import logging
import os

_logger = logging.getLogger(__name__)
def migrate(cr, version):
    cr.execute("SELECT count(*) FROM product_template WHERE type='consu' AND NOT tracking='none'")
    if cr.fetchone()[0]:
        _logger.warning("Consumable tracked products is not possible Anymore.")
        if os.environ.get('ODOO_MIG_STOCK_TRACK_CONSUMABLE_PRODUCT'):
            cr.execute("""
                UPDATE product_template
                   SET type='product'
                 WHERE type='consu' AND NOT tracking='none'
            """)
        else:
            cr.execute("""
                UPDATE product_template
                   SET tracking='none'
                 WHERE type='consu' AND NOT tracking='none'
            """)
