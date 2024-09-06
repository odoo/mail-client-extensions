from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    mapping = {
        "pain.001.001.03.se": env["account.payment.method"].search([("code", "=", "iso20022_se")], limit=1),
        "pain.001.001.03.ch.02": env["account.payment.method"].search([("code", "=", "iso20022_ch")], limit=1),
        "iso_20022": env["account.payment.method"].search([("code", "=", "iso20022")], limit=1),
    }

    sct_payment_method_id = util.ref(cr, "account_iso20022.account_payment_method_sepa_ct")

    for old_selection_value, payment_method in mapping.items():
        cr.execute(
            """
                UPDATE account_payment_method_line pmt_meth_line
                SET payment_method_id=%s, name=%s
                FROM account_journal journal
                WHERE journal.id = pmt_meth_line.journal_id
                AND journal.sepa_pain_version = %s
                AND pmt_meth_line.payment_method_id = %s
            """,
            [
                payment_method.id,
                payment_method.name,
                old_selection_value,
                sct_payment_method_id,
            ],
        )

    cr.execute(
        """
            UPDATE account_payment pmt
            SET iso20022_uetr = gen_random_uuid()
            FROM account_journal journal, account_move move
            WHERE journal.id = pmt.journal_id
            AND move.id = pmt.move_id
            AND payment_method_id = %s
            AND journal.sepa_pain_version = 'pain.001.001.03'
            AND pmt.iso20022_uetr IS NULL
            AND NOT COALESCE(move.is_move_sent, false)
        """,
        [sct_payment_method_id],
    )
