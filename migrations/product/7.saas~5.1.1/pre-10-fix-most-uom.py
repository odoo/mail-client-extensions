import logging

from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.product.saas-5.'
_logger = logging.getLogger(NS + __name__)

def fix_uom_factor_lack_precision(cr):
    cr.execute("""
        UPDATE  product_uom
        SET     factor = 1.0 / round(1.0 / factor, 4)
        WHERE   factor != 0
        AND     round(1.0 / factor, 4) != 0
        AND     abs((1.0 / round(1.0 / factor, 4)) - factor) != 0
        AND     abs((1.0 / round(1.0 / factor, 4)) - factor) < 1e-06
        RETURNING id, name, factor;
        """, [])
    for id, name, factor in cr.fetchall():
        _logger.info("[UoM %s (%s) must be more accurate] factor is now %s",
                     id, name, factor)

def migrate(cr, version):
    fix_uom_factor_lack_precision(cr)
