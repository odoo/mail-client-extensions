# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
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
        SELECT
            pajm.journal_id,
            apm.id AS payment_method_id,
            pajm.name,
            CASE WHEN apm.payment_type = 'inbound' THEN jam.inbound_account_id ELSE jam.outbound_account_id END
            AS payment_account_id
          FROM _upg_payment_acquirer_journal_mapping pajm
          JOIN payment_acquirer acquirer ON pajm.id = acquirer.id
          JOIN account_payment_method apm ON apm.code = acquirer.provider
     LEFT JOIN _upg_journal_accounts_mapping jam ON jam.journal_id = pajm.journal_id
    """
    )
    if cr.rowcount:
        env["account.payment.method.line"].create(cr.dictfetchall())
        # Flush the lines to trigger the computes, since the computed fields are needed later to migrate the payments.
        env["account.payment.method.line"].flush()

    cr.execute("DROP TABLE _upg_journal_accounts_mapping")
    cr.execute("DROP TABLE _upg_payment_acquirer_journal_mapping")

    # ===============================================================
    # Payment method improvements (PR: 72105(odoo), 18981(enterprise))
    # ===============================================================
    query = """
        UPDATE account_payment ap
           SET payment_method_line_id = apml.id
          FROM account_payment_method_line apml
          JOIN _upg_account_payment_payment_method_mapping map
            ON ((map.payment_method_id IS NULL AND apml.payment_acquirer_id IS NOT NULL)
            OR apml.payment_method_id = map.payment_method_id)
           AND apml.journal_id = map.journal_id
         WHERE map.id = ap.id
         """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", alias="ap"))

    # We can still have payments without method lines.
    # It could happen for payments linked to the electronic method, but not a payment acquirer journal
    # In such case, we'll link them to the manual method of the linked journal
    query = """
        UPDATE account_payment ap
           SET payment_method_line_id = apml.id
          FROM account_payment_method_line apml
          JOIN _upg_account_payment_payment_method_mapping map ON apml.journal_id = map.journal_id
          JOIN account_payment_method apm ON apm.id = apml.payment_method_id
         WHERE ap.payment_method_line_id IS NULL
           AND map.id = ap.id
           AND apm.payment_type = ap.payment_type
           AND apm.code = 'manual'
         """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", alias="ap"))

    cr.execute("DROP TABLE _upg_account_payment_payment_method_mapping")

    # Get a structure giving us, for each acquirers appearing multiple times,
    # The state of all the acquirers of a provider and the id's of their apml.
    # Then, unlink the apml using the orm to make sure they are properly handled
    # (either their journal_id is removed, or they are completely deleted)
    cr.execute(
        """
        SELECT apml.id
          FROM account_payment_method_line apml
          JOIN account_journal j
            ON apml.journal_id = j.id
          JOIN account_payment_method apm
            ON apm.id = apml.payment_method_id
          JOIN payment_acquirer acquirer
            ON apm.code = acquirer.provider
           AND j.company_id = acquirer.company_id
      GROUP BY apml.id
        HAVING bool_and(acquirer.state NOT IN ('enabled', 'test'))
        """
    )
    if cr.rowcount:
        env["account.payment.method.line"].search([("id", "in", [lid for lid, in cr.fetchall()])]).unlink()
