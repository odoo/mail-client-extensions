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

    if cr._cnx.server_version < 130000:
        # Postgres 12 is missing the `gen_random_uuid()` function. Define one.
        func = """
            CREATE FUNCTION gen_random_uuid()
            RETURNS uuid as $body$
                SELECT string_agg(
                           CASE i
                               WHEN 13 THEN '4' -- uuid4 spec
                               WHEN 17 THEN to_hex(8 + width_bucket(random(), 0, 1, 4) - 1)  -- uuid4 spec, random from 8,9,10,11
                               ELSE to_hex(width_bucket(random(), 0, 1, 16) - 1) -- random hex value
                           END,
                           ''
                       )::uuid
                  FROM generate_series(1, 32) as data(i);
            $body$
            LANGUAGE 'sql'
            VOLATILE
        """
        cr.execute(func)

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
