from odoo.upgrade import util


def migrate(cr, version):
    # ===========================================================
    # Task 2567701 : Move Sepa Pain Version
    # ===========================================================
    util.remove_field(cr, "res.company", "sepa_pain_version")
    util.remove_field(cr, "res.config.settings", "sepa_pain_version")
    util.create_column(cr, "account_journal", "sepa_pain_version", "varchar")

    # Ref: https://github.com/odoo/enterprise/blob/fd519260d93e76bafd5de08acf4bbfa6450e63f2/account_sepa/models/account_journal.py#L62-L77
    # First try to retrieve the country_code from the IBAN
    cr.execute(
        """
        UPDATE account_journal j
           SET sepa_pain_version = CASE substring(b.acc_number, 1, 2)
                   WHEN 'DE' THEN 'pain.001.003.03'
                   WHEN 'CH' THEN 'pain.001.001.03.ch.02'
                   WHEN 'SE' THEN 'pain.001.001.03.se'
                   WHEN 'AT' THEN 'pain.001.001.03.austrian.004'
                   ELSE 'pain.001.001.03'
               END
          FROM res_partner_bank b
         WHERE j.bank_account_id = b.id
           AND b.acc_number ~ '^[A-Z]{2}[0-9]{2}.*'
        """
    )
    # Then try from the company's fiscal country, and finally from the company's country
    cr.execute(
        """
        UPDATE account_journal j
           SET sepa_pain_version = CASE COALESCE(fiscal_c.code, comp_c.code)
                   WHEN 'DE' THEN 'pain.001.003.03'
                   WHEN 'CH' THEN 'pain.001.001.03.ch.02'
                   WHEN 'SE' THEN 'pain.001.001.03.se'
                   WHEN 'AT' THEN 'pain.001.001.03.austrian.004'
                   ELSE 'pain.001.001.03'
               END
          FROM res_company c
          JOIN res_partner p
            ON p.id = c.partner_id
     LEFT JOIN res_country fiscal_c
            ON c.account_fiscal_country_id = fiscal_c.id
     LEFT JOIN res_country comp_c
            ON p.country_id = comp_c.id
         WHERE j.sepa_pain_version IS NULL
           AND j.company_id = c.id
        """
    )
