def migrate(cr, version):
    # To maintain old manufacture rules behavior, we need to pre-set location_dest_from_rule on existing
    # manufacture rules that have different destinations than their picking types.
    cr.execute(
        """
        UPDATE stock_rule sr
           SET location_dest_from_rule = true
          FROM stock_picking_type spt
         WHERE spt.id = sr.picking_type_id
           AND sr.action = 'manufacture'
           AND sr.location_dest_id IS DISTINCT FROM spt.default_location_dest_id
    """
    )
