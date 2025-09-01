# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE res_partner_bank SET sequence = s.seq
        FROM (
            SELECT id, COALESCE(sequence, (
                    SELECT coalesce(max(sequence),0)
                    FROM res_partner_bank
                    WHERE partner_id = b.partner_id) + row_number() OVER(PARTITION BY partner_id ORDER BY sequence, id)) AS seq
            FROM res_partner_bank b
        ) AS s
        WHERE
            s.id = res_partner_bank.id
        AND
            res_partner_bank.sequence is NULL
    """)
