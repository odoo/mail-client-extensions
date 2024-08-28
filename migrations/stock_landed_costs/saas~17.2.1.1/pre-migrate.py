from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr, "stock_landed_cost", "company_id", "int4", fk_table="res_company", on_delete_action="RESTRICT"
    )
    query = """
        UPDATE stock_landed_cost cost
           SET company_id = journal.company_id
          FROM account_journal journal
         WHERE cost.account_journal_id = journal.id
           AND cost.company_id IS NULL
    """
    util.explode_execute(cr, query, table="stock_landed_cost", alias="cost")
