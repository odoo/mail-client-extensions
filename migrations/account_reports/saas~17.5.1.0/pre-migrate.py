from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "exclude_bank_lines", "bool")
    query_exclude_bank_lines = """
        UPDATE account_move_line aml
           SET exclude_bank_lines = TRUE
          FROM account_journal journal
         WHERE aml.journal_id = journal.id
           AND journal.default_account_id != aml.account_id
    """
    util.explode_execute(cr, query_exclude_bank_lines, table="account_move_line", alias="aml")

    util.remove_field(cr, "account.move", "tax_closing_show_multi_closing_warning")
