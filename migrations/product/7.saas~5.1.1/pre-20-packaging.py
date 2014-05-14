from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        The weight, length, width, height fields, ... need to be moved to a product_ul 
    """
    #Create temporary fields that can be used later in post for creating the necessary pallets, ...
    util.rename_field(cr, 'product_packaging', 'height', '_height')
    util.rename_field(cr, 'product_packaging', 'width', '_width')
    util.rename_field(cr, 'product_packaging', 'length', '_length')
    util.rename_field(cr, 'product_packaging', 'weight', '_weight')
    util.rename_field(cr, 'product_packaging', 'weight_ul', '_weight_ul')