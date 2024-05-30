from odoo.upgrade import util


def migrate(cr, version):
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
