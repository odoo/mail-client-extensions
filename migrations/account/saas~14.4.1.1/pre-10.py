# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_tax_group", "country_id", "int4")

    # Use the ir_model_data table to try and fill as many country_id as possible for the tax groups coming from the XML files
    # To do that, we look into the module that created the tax group and tries to match as many as possible by getting the
    # country code from it, while avoiding error such as l10n_generic_coa returning ge => Georgia
    cr.execute(
        """
        WITH subquery AS (
               SELECT tg.res_id AS group_id, country.id AS country_id
                 FROM ir_model_data tg
                 JOIN res_country country ON lower(country.code) = (regexp_match(tg.module, '^l10n_(..)(?:$|_)'))[1]
                WHERE tg.model = 'account.tax.group'
        )
        UPDATE account_tax_group SET country_id = sq.country_id FROM subquery sq WHERE account_tax_group.id = sq.group_id;
    """
    )

    # For tax groups which have a country_id, but also taxes in another country, remove the country_id to make it available
    # to all countries.
    cr.execute(
        """
        UPDATE account_tax_group
           SET country_id = NULL
         WHERE id IN (
               SELECT tax_group_id
                 FROM account_tax
             GROUP BY tax_group_id
               HAVING count(DISTINCT country_id) > 1
        )
    """
    )

    # For tax groups with no country_id but which have taxes all in the same country, update it to use that country_id.
    cr.execute(
        """
        WITH mono_country AS (
          SELECT tax_group_id, min(country_id) as country_id
            FROM account_tax
        GROUP BY tax_group_id
          HAVING count(DISTINCT country_id) = 1
        )
        UPDATE account_tax_group g
           SET country_id = m.country_id
          FROM mono_country m
         WHERE m.tax_group_id = g.id
           AND g.country_id IS NULL
    """
    )

    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================
    util.remove_field(cr, "account.journal", "at_least_one_inbound")
    util.remove_field(cr, "account.journal", "at_least_one_outbound")
    util.remove_field(cr, "account.payment.method", "sequence")

    util.create_column(cr, "account_payment", "outstanding_account_id", "int4")

    query = """
        UPDATE account_payment p
           SET outstanding_account_id = CASE WHEN p.payment_type = 'inbound'
                                             THEN j.payment_debit_account_id
                                             ELSE j.payment_credit_account_id
                                         END
          FROM account_move m
          JOIN account_journal j ON j.id = m.journal_id
         WHERE m.id = p.move_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", prefix="p."))

    # Backup the relation between the journals and the payment methods to create the lines later on.
    cr.execute(
        """
        CREATE TABLE _upg_account_payment_method_mapping AS (
            SELECT rel.journal_id, apm.id AS apm_id, apm.payment_type
              FROM account_journal_inbound_payment_method_rel rel
              JOIN account_payment_method apm ON apm.id = rel.inbound_payment_method
             WHERE apm.code != 'electronic'

            UNION

            SELECT rel.journal_id, apm.id AS apm_id, apm.payment_type
              FROM account_journal_outbound_payment_method_rel rel
              JOIN account_payment_method apm ON apm.id = rel.outbound_payment_method
        )
        """
    )

    # Backup the relation between the journals, and their debit/credit accounts to set them back up on the payment method lines
    # if they are different from the default accounts on the company
    cr.execute(
        """
        CREATE TABLE _upg_journal_accounts_mapping AS (

            SELECT x.id as journal_id,
                   max(inbound_account_id) as inbound_account_id,
                   max(outbound_account_id) as outbound_account_id
              FROM (
                SELECT j.id, j.payment_debit_account_id as inbound_account_id, NULL as outbound_account_id
                  FROM account_journal j
                  JOIN res_company c ON c.id = j.company_id
                 WHERE j.payment_debit_account_id IS DISTINCT FROM c.account_journal_payment_debit_account_id

                UNION

                SELECT j.id, NULL as inbound_account_id, j.payment_credit_account_id as outbound_account_id
                  FROM account_journal j
                  JOIN res_company c ON c.id = j.company_id
                 WHERE j.payment_credit_account_id IS DISTINCT FROM c.account_journal_payment_credit_account_id

              ) x
          GROUP BY x.id
        )
        """
    )

    util.remove_field(cr, "account.journal", "inbound_payment_method_ids")
    util.remove_field(cr, "account.journal", "outbound_payment_method_ids")
    util.remove_field(cr, "account.journal", "payment_debit_account_id")
    util.remove_field(cr, "account.journal", "payment_credit_account_id")

    # ===============================================================
    # Payment method improvements (PR: 72105(odoo), 18981(enterprise))
    # ===============================================================
    util.rename_field(cr, "account.payment", "hide_payment_method", "hide_payment_method_line")
    util.rename_field(cr, "account.payment.register", "hide_payment_method", "hide_payment_method_line")

    util.remove_field(cr, "account.payment", "available_payment_method_ids")

    util.remove_field(cr, "account.payment.register", "payment_method_id")
    util.create_column(cr, "account_payment_register", "payment_method_line_id", "int4")

    util.remove_field(cr, "account.payment.register", "available_payment_method_ids")

    # Backup the relationship between payment and payment method in a temp table.
    # Then set all payment method to False, to avoid issues when the upgrade
    # process change the foreign key of the column to payment_method_line_id

    # The electronic method disappear during the migration, so we make sure to not get the id
    # so that we can properly look for the line corresponding to the acquirer later on.
    cr.execute(
        """
        CREATE TABLE _upg_account_payment_payment_method_mapping AS (
            SELECT ap.id,
                CASE WHEN apm.code != 'electronic'
                     THEN ap.payment_method_id
                     ELSE NULL
                   END AS payment_method_id, am.journal_id
              FROM account_payment ap
              JOIN account_move am ON ap.id = am.payment_id
              JOIN account_payment_method apm ON ap.payment_method_id = apm.id
        )
        """
    )
    util.create_column(cr, "account_payment", "payment_method_line_id", "int4")
