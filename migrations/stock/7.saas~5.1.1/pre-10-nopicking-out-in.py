from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    #Views delete
    util.remove_record(cr, 'stock.view_picking_in_tree')
    util.remove_record(cr, 'stock.view_picking_in_form')
    util.remove_record(cr, 'stock.view_picking_in_calendar')

    util.remove_record(cr, 'stock.view_picking_out_tree')
    util.remove_record(cr, 'stock.view_picking_out_form')
    util.remove_record(cr, 'stock.view_picking_out_calendar')

    #Change stock.picking.in/out to stock.picking
    cr.execute("SELECT model, id FROM ir_model WHERE model IN %s",
               (('stock.picking', 'stock.picking.in', 'stock.picking.out'),)
    )
    
    ids = dict(cr.fetchall())
    id_sp = ids['stock.picking']
    id_in = ids['stock.picking.in']
    id_out = ids['stock.picking.out']
    
    cr.execute("DELETE FROM ir_model_fields WHERE model_id IN %s RETURNING id", ((id_in, id_out),))
    fields_ids = tuple(x[0] for x in cr.fetchall())
    cr.execute("DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s", ('ir.model.fields', fields_ids))
    cr.execute("DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s", ('ir.model', (id_in, id_out)))
    util.replace_record_references(cr, ('ir.model', id_in), ('ir.model', id_sp))
    util.replace_record_references(cr, ('ir.model', id_out), ('ir.model', id_sp))
    cr.execute("DELETE FROM ir_model WHERE id IN %s", ((id_in, id_out),))
    
    util.rename_model(cr, 'stock.picking.out', 'stock.picking', rename_table=False)
    util.rename_model(cr, 'stock.picking.in', 'stock.picking', rename_table=False)

    # Some databases have a size on `state` field. Don't know where this from, but this will
    # forbid to insert new state `partially_available` which is longer than 16 characters.
    cr.execute("ALTER TABLE stock_picking ALTER COLUMN state TYPE character varying")
