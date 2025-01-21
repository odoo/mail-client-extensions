def migrate(cr, version):
    # Set the right code for dropship's pickings.
    query = """
        UPDATE stock_picking_type ptype
           SET code = 'dropship'
          FROM ir_sequence seq
         WHERE ptype.sequence_id = seq.id
           AND seq.code = 'stock.dropshipping'
    """
    cr.execute(query)
