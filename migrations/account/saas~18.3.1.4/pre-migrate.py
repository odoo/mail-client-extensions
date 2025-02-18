from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "incoming_einvoice_notification_email", "varchar")
    cr.execute(
        """
        UPDATE account_journal AS j
           SET incoming_einvoice_notification_email = c.email
          FROM res_company AS c
         WHERE c.id = j.company_id;
        """
    )

    util.create_column(cr, "account_bank_statement", "currency_id", "integer")
    util.explode_execute(
        cr,
        """
         UPDATE account_bank_statement AS s_up
           SET currency_id = COALESCE(j.currency_id, c.currency_id)
          FROM account_bank_statement AS s
     LEFT JOIN account_journal AS j
            ON (s.journal_id = j.id)
     LEFT JOIN res_company AS c
            ON (j.company_id = c.id)
         WHERE s_up.id = s.id
        """,
        table="account_bank_statement",
        alias="s_up",
    )

    util.remove_field(cr, "res.partner", "debit_limit")
    util.remove_field(cr, "res.partner", "journal_item_count")

    util.remove_field(cr, "res.partner", "invoice_warn")
    util.remove_field(cr, "res.partner", "invoice_warn_msg")
    util.remove_field(cr, "res.config.settings", "group_warning_account")
    util.remove_group(cr, "account.group_warning_account")
