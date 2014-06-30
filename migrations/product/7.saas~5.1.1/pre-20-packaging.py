from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        The weight, length, width, height fields, ... need to be moved to a product_ul
    """
    #Create temporary fields that can be used later in post for creating the necessary pallets, ...
    #Maybe not needed as it is not changed by something else
    util.rename_field(cr, 'product.packaging', 'height', '_height')
    util.rename_field(cr, 'product.packaging', 'width', '_width')
    util.rename_field(cr, 'product.packaging', 'length', '_length')
#    util.rename_field(cr, 'product_packaging', 'weight', '_weight')
    util.rename_field(cr, 'product.packaging', 'weight_ul', '_weight_ul')
    
    # Packaging is on product template and not on product variant
    util.create_column(cr, 'product_packaging', 'product_tmpl_id', 'int4')
    cr.execute("""
    UPDATE product_packaging SET product_tmpl_id = pp.product_tmpl_id FROM product_product pp
    WHERE product_packaging.product_id = pp.id
    """)