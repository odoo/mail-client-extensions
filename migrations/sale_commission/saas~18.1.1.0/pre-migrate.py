def migrate(cr, version):
    cr.execute("DROP INDEX IF EXISTS account_move_team_id_date_idx")
    cr.execute("DROP INDEX IF EXISTS account_move_invoice_user_id_date_idx")
