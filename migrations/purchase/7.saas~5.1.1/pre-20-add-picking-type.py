from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
    Field 'picking_type_id' is added in saas-5, Prevent the default value to be calculated during the migration and add NOT NULL constraint.
    """
    util.create_column(cr, 'purchase_order', 'picking_type_id', 'int4')
    cr.execute("""
        UPDATE purchase_order SET picking_type_id = (select id from stock_picking_type where code = 'incoming' limit 1);
        ALTER TABLE purchase_order ALTER COLUMN picking_type_id SET NOT NULL;
        """)
