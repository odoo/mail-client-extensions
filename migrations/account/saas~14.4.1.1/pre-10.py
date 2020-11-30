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
