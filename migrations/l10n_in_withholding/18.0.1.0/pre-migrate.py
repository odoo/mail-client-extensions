from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_in_withholding_ref_payment_id", "int4")
    util.explode_execute(
        cr,
        """
        UPDATE account_move am
           SET l10n_in_withholding_ref_payment_id = ap.id
          FROM account_payment ap
         WHERE am.l10n_in_withholding_ref_move_id = ap.move_id
           AND {parallel_filter}
        """,
        table="account_move",
        alias="am",
    )
