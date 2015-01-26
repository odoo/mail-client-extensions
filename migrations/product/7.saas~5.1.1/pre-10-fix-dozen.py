import logging

from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.product.saas-5.'
_logger = logging.getLogger(NS + __name__)

def fix_dozen(cr):
    # fix usual small issue with UoM dozen
    cr.execute("""
        UPDATE product_uom SET factor = (1.0 / 12.0) WHERE id = %s
        RETURNING id, factor
        """, [util.ref(cr, 'product.product_uom_dozen')])
    _logger.info("[UoM %s (dozen) must be more accurate] factor is now %s",
                 *cr.fetchone())

def migrate(cr, version):
    fix_dozen(cr)
