from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Puts cost price and methods in properties where price is not 0 and cost method does not equal 'standard'
    It is doing this for company 1, but should do this for all companies?
    """
    util.rename_field(cr, 'product_product', 'valuation', '_valuation_mig')
