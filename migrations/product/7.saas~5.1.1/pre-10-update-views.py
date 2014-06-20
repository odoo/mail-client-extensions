from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """As deleted xmlid are deleted only at the end of the update, deleted
       views still exists in database during the update process and used when
       applying the view inheritance. If the views use a deleted field,
       this raise an error. We delete it ourself to avoid this.
    """
    util.remove_record(cr, 'product.product_normal_form_view')
    util.remove_record(cr, 'product.product_category_form_view')


    util.move_field_to_other_module(cr, 'product.template', 'track_production', 'mrp')
