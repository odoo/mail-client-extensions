# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================
    util.delete_unused(cr, "payment.account_payment_method_electronic_in")
    util.remove_field(cr, "account.payment", "related_partner_ids")
    util.remove_field(cr, "account.payment.register", "suitable_payment_token_partner_ids")

    cr.execute(
        """
            CREATE TABLE _upg_payment_acquirer_journal_mapping AS (
                SELECT id, journal_id
                  FROM payment_acquirer
                 WHERE journal_id IS NOT NULL
            )
        """
    )

    util.remove_column(cr, "payment_acquirer", "journal_id")  # now computed
