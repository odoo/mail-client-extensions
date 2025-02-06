from odoo.upgrade import util


def migrate(cr, version):
    # removed in `end` because it is used by `l10n_in` upgrade script.
    util.make_field_non_stored(cr, "account.account", "code", selectable=True)

    util.remove_column(cr, "res_company", "account_journal_payment_debit_account_id")
    util.remove_column(cr, "res_company", "account_journal_payment_credit_account_id")
