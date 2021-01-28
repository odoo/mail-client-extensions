# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError

from odoo.addons.base_iban.models.res_partner_bank import normalize_iban, pretty_iban
from odoo.addons.l10n_ch.models.res_bank import validate_qr_iban


def migrate(cr, version):
    cr.execute("""
        SELECT res_partner_bank.id, res_partner_bank.acc_number
        FROM res_company
        JOIN res_partner_bank ON res_partner_bank.partner_id = res_company.partner_id
        WHERE res_partner_bank.l10n_ch_qr_iban IS NULL
    """)

    for partner_bank_id, acc_number in cr.fetchall():
        try:
            validate_qr_iban(acc_number)
        except ValidationError:
            continue

        cr.execute("""
            UPDATE res_partner_bank
            SET l10n_ch_qr_iban = %s
            WHERE id = %s
        """, (
            pretty_iban(normalize_iban(acc_number)),
            partner_bank_id,
        ))
