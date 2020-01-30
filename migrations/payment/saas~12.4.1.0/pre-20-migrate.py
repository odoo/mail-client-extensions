# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "check_validity", "boolean")

    cr.execute("""
        UPDATE
            payment_token SET partner_id = p.partner_id
        FROM
            payment_transaction AS p
        WHERE
                payment_token.id = p.payment_token_id
            AND
                payment_token.partner_id =
                    (select res_id from ir_model_data where name = 'public_partner' and module = 'base')
    """)
    cr.execute("""
        UPDATE
            payment_token SET partner_id = (select res_id from ir_model_data where name = 'partner_root' and module = 'base')
        WHERE partner_id =
                (select res_id from ir_model_data where name = 'public_partner' and module = 'base')
    """)

