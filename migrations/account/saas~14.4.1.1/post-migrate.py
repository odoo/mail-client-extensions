# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================

    # Get all the journal, their payment methods as well as the optional account if needed,
    # Then create the payment method lines in the journals
    cr.execute(
        """
        SELECT apmm.journal_id, unnest(array_agg(apmm.apm_id)),
               CASE WHEN apmm.payment_type = 'inbound' THEN jam.inbound_account_id ELSE jam.outbound_account_id END
          FROM _upg_account_payment_method_mapping apmm
     LEFT JOIN _upg_journal_accounts_mapping jam ON jam.journal_id = apmm.journal_id
      GROUP BY apmm.journal_id, apmm.payment_type, jam.inbound_account_id, jam.outbound_account_id
    """
    )

    if cr.rowcount:
        util.env(cr)["account.payment.method.line"].create(
            [
                {"payment_method_id": method_id, "journal_id": journal_id, "payment_account_id": account_id}
                for journal_id, method_id, account_id in cr.fetchall()
            ]
        )

    cr.execute("DROP TABLE _upg_account_payment_method_mapping")

    if not util.module_installed(cr, "payment"):
        cr.execute("DROP TABLE _upg_journal_accounts_mapping")

        query = """
            UPDATE account_payment ap
               SET payment_method_line_id = apml.id
              FROM account_payment_method_line apml
              JOIN _upg_account_payment_payment_method_mapping map ON apml.payment_method_id = map.payment_method_id
                                                                  AND apml.journal_id = map.journal_id
             WHERE map.id = ap.id
             """
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", prefix="ap."))

        cr.execute("DROP TABLE _upg_account_payment_payment_method_mapping")
