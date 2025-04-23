def migrate(cr, version):
    cr.execute("DROP INDEX IF EXISTS account_move_line__unreconciled_index")
