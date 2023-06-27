def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM account_asset a
             USING asset_move_line_rel rel
              JOIN account_move_line line
                ON line.id = rel.line_id
              JOIN account_move move
                ON move.id = line.move_id
             WHERE a.id = rel.asset_id
               AND a.state = 'draft'
               AND move.state = 'draft'
        """
    )
