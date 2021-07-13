# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================
    util.delete_unused(cr, "payment.account_payment_method_electronic_in")
    util.remove_field(cr, "account.payment", "related_partner_ids")
    util.remove_field(cr, "account.payment.register", "suitable_payment_token_partner_ids")

    # Do not create payment method lines for disabled acquirers.
    # The user will have to set the journal back when he will want to reactivate it
    # and the line will be created for him.
    cr.execute(
        """
            CREATE TABLE _upg_payment_acquirer_journal_mapping AS (
                SELECT id, journal_id, name
                  FROM payment_acquirer
                 WHERE journal_id IS NOT NULL
            )
        """
    )

    # Make sure that we do not have duplicated name for the same journal in the temp table.
    # This could happen if two acquirers having the same name, are both active on the same journal.

    # Also do it for SEPA Direct Debit because the acquirer has the same name as the SEPA Direct Debit payment method
    cr.execute(
        """
        WITH sub AS (
            SELECT id, COUNT(name) OVER (PARTITION BY name ORDER BY id) AS nb
              FROM _upg_payment_acquirer_journal_mapping
             WHERE name IN (
                SELECT name
                  FROM _upg_payment_acquirer_journal_mapping
              GROUP BY journal_id, name
                HAVING array_length(array_agg(id), 1) > 1
            ) OR name = 'SEPA Direct Debit'
        )
        UPDATE _upg_payment_acquirer_journal_mapping map
           SET name = map.name || ' - ' || sub.nb
          FROM sub
         WHERE map.id = sub.id
        """
    )

    util.remove_column(cr, "payment_acquirer", "journal_id")  # now computed

    # ===============================================================
    # Payment method improvements (PR: 72105(odoo), 18981(enterprise))
    # ===============================================================

    util.create_column(cr, "account_payment_method_line", "payment_acquirer_id", "int4")
