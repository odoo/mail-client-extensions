from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "sale_lock_date", "date")
    util.create_column(cr, "res_company", "purchase_lock_date", "date")
    cr.execute(
        """
        UPDATE res_company c
           SET sale_lock_date = c.period_lock_date,
               purchase_lock_date = c.period_lock_date
         WHERE c.period_lock_date IS NOT NULL
        """,
    )
    util.remove_field(cr, "res.company", "period_lock_date")
    util.remove_field(cr, "res.company", "max_tax_lock_date")

    util.rename_field(cr, "account.move", "made_sequence_hole", "made_sequence_gap")
    util.create_column(cr, "account_move", "made_sequence_gap", "bool")

    query = """
        WITH to_update AS (
            SELECT this.id
              FROM account_move this
         LEFT JOIN account_move other ON this.journal_id = other.journal_id
                                     AND this.sequence_prefix = other.sequence_prefix
                                     AND this.sequence_number = other.sequence_number + 1
             WHERE other.id IS NULL
               AND this.sequence_number != 1
               AND this.name != '/'
               AND {parallel_filter}
        )
        UPDATE account_move
           SET made_sequence_gap = TRUE
          FROM to_update
         WHERE account_move.id = to_update.id
    """
    util.explode_execute(cr, query, table="account_move", alias="this")
    cr.execute("DROP INDEX IF EXISTS account_move_sequence_index3")
    util.rename_field(cr, "account.move", "reversal_move_id", "reversal_move_ids")
    util.remove_record(cr, "account.invoice_send")

    # Autopost bills
    util.create_column(cr, "account_move", "is_manually_modified", "bool", default=True)
    util.create_column(cr, "res_partner", "autopost_bills", "varchar", default="ask")
    util.create_column(cr, "res_company", "autopost_bills", "bool", default=True)
