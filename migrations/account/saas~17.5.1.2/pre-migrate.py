from odoo.tools import SQL

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

    util.create_column(cr, "account_move", "preferred_payment_method_line_id", "int4")
    if util.column_exists(cr, "account_move", "preferred_payment_method_id"):
        # Create a mapping for payment_method and a payment method line
        query = """
            WITH pay_lines AS (
                SELECT l.payment_method_id,
                       j.company_id,
                       min(l.id) AS payment_method_line_id
                  FROM account_payment_method_line l
                  JOIN account_journal j
                    ON j.id = l.journal_id
              GROUP BY l.payment_method_id, j.company_id
            )
          UPDATE account_move am
             SET preferred_payment_method_line_id = pl.payment_method_line_id
            FROM pay_lines pl
           WHERE am.preferred_payment_method_id = pl.payment_method_id
             AND am.company_id = pl.company_id
        """
        util.explode_execute(cr, query, table="account_move", alias="am")

    # Share accounts between companies
    # 1. Populate ir_property with account codes
    cr.execute("SELECT id FROM ir_model_fields WHERE model='account.account' AND name='code'")
    [fields_id] = cr.fetchone()
    cr.execute(
        SQL(
            """
        INSERT INTO ir_property (name, res_id, company_id, fields_id, value_text, type)
             SELECT 'code' AS name,
                    'account.account,' || account_account.id AS res_id,
                    SPLIT_PART(res_company.parent_path, '/', 1)::int AS company_id,
                    %s AS fields_id,
                    account_account.code AS value_text,
                    'char' AS type
               FROM account_account
               JOIN res_company ON res_company.id = account_account.company_id
    """,
            fields_id,
        )
    )
    util.remove_column(cr, "account_account", "code")

    # 2. Create and populate account_account_res_company_rel
    util.create_m2m(cr, "account_account_res_company_rel", "account_account", "res_company")
    cr.execute("""
        INSERT INTO account_account_res_company_rel (account_account_id, res_company_id)
             SELECT id AS account_account_id,
                    company_id AS res_company_id
               FROM account_account
    """)
    util.rename_field(cr, "account.account", "company_id", "company_ids")
    util.remove_column(cr, "account_account", "company_ids")

    # 3. Misc column/field changes
    util.remove_column(cr, "account_account", "group_id")
    util.remove_column(cr, "account_account", "root_id")
    util.remove_column(cr, "account_move_line", "account_root_id")
    cr.execute('DROP VIEW IF EXISTS "account_root" CASCADE')
    util.remove_field(cr, "account.root", "company_id")
    util.remove_record(cr, "account.account_root_comp_rule")
    util.remove_field(cr, "account.cash.rounding", "company_id")
