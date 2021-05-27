# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================

    # During the installation of the acquirers payment methods, method lines will be added for them in the default bank journal.
    # We'll remove these before migrating properly to the journals that were set up on the acquirers before the migration
    cr.execute(
        """
        DELETE FROM account_payment_method_line apml
              USING account_payment_method apm
              WHERE apm.id = apml.payment_method_id
                AND apm.code IN (SELECT provider FROM payment_acquirer)
        """
    )

    # Get every pair of journals and their linked acquirer as well as the optional account,
    # to then create the related payment method lines accordingly.
    cr.execute(
        """
        SELECT pajm.journal_id, apm.id,
               CASE WHEN apm.payment_type = 'inbound' THEN jam.inbound_account_id ELSE jam.outbound_account_id END
          FROM _upg_payment_acquirer_journal_mapping pajm
          JOIN payment_acquirer acquirer ON pajm.id = acquirer.id
          JOIN account_payment_method apm ON apm.code = acquirer.provider
     LEFT JOIN _upg_journal_accounts_mapping jam ON jam.journal_id = pajm.journal_id
    """
    )

    if cr.rowcount:
        util.env(cr)["account.payment.method.line"].create(
            [
                {"payment_method_id": payment_method_id, "journal_id": journal_id, "payment_account_id": account_id}
                for journal_id, payment_method_id, account_id in cr.fetchall()
            ]
        )

    cr.execute("DROP TABLE _upg_journal_accounts_mapping")
    cr.execute("DROP TABLE _upg_payment_acquirer_journal_mapping")
