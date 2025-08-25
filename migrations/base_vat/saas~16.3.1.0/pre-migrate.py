from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "vies_failed_message")
    util.create_column(cr, "res_partner", "vies_valid", "boolean")
    europe_group_id = util.ref(cr, "base.europe")

    eu_country_codes = (
        "AT",
        "BE",
        "BG",
        "CY",
        "CZ",
        "DE",
        "DK",
        "EE",
        "ES",
        "FI",
        "FR",
        "GR",
        "HR",
        "HU",
        "IE",
        "IT",
        "LT",
        "LU",
        "LV",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SE",
        "SI",
        "SK",
        "XI",
        "EL",
        "AK",
        "MC",
    )

    update_partner_query = cr.mogrify(
        """
        WITH vies_fiscal_position AS (
            SELECT fp.id
              FROM account_fiscal_position fp
         LEFT JOIN account_fiscal_position_tax fp_tax ON fp_tax.position_id = fp.id
         LEFT JOIN account_tax tax ON tax.id = fp_tax.tax_dest_id
             WHERE fp.vat_required IS TRUE
               AND fp.auto_apply IS TRUE
               AND fp.foreign_vat IS NULL
               AND (tax.type_tax_use = 'sale' OR tax.id IS NULL)
               AND fp.country_group_id = %s
          GROUP BY fp.id, fp.name
            HAVING bool_and(COALESCE(tax.amount, 0) = 0)
        ),
        partner_to_check AS (
            SELECT partner.id AS partner_id
              FROM account_move move
              JOIN res_partner partner ON move.partner_id = partner.id
              JOIN res_company company ON company.id = move.company_id
              JOIN res_country company_country ON company.account_fiscal_country_id = company_country.id
         LEFT JOIN res_country partner_country ON  partner.country_id = partner_country.id
             WHERE partner.vat IS NOT NULL
                   AND company_country.code IN %s
                   AND (UPPER(SUBSTRING(partner.vat, 1, 2)) IN %s
                        OR NOT EXISTS (
                            SELECT 1
                              FROM res_country
                             WHERE code ILIKE SUBSTRING(partner.vat, 1, 2)
                               AND partner_country.code IN %s
                        )
                   )
             GROUP BY partner.id
               HAVING {parallel_filter}
        )
        UPDATE res_partner partner
           SET vies_valid = recent_move.vies_valid
          FROM partner_to_check JOIN LATERAL (
                  SELECT CASE WHEN(
                              fp.id IS NOT NULL OR (
                                  move.fiscal_position_id IS NULL
                                  AND move.amount_tax = 0
                                  AND move_type = 'out_invoice'
                              )
                         ) THEN TRUE ELSE FALSE END AS vies_valid,
                         move.partner_id
                    FROM account_move move
               LEFT JOIN vies_fiscal_position fp ON fp.id = move.fiscal_position_id
                   WHERE move.partner_id = partner_to_check.partner_id
                     AND move.state = 'posted'
                     AND move.invoice_date IS NOT NULL
                ORDER BY move.invoice_date DESC
                   LIMIT 1
               ) recent_move ON TRUE
         WHERE partner.id = partner_to_check.partner_id
    """,
        (europe_group_id, eu_country_codes, eu_country_codes, eu_country_codes),
    )
    util.explode_execute(cr, update_partner_query.decode(), table="res_partner", alias="partner")

    # Now add a message for each of the partners that had their vies_valid set
    cr.execute(
        """
            INSERT INTO mail_message(
                model, res_id, record_name, author_id, message_type, body, subtype_id
            )
                 SELECT 'res.partner',
                        p.id,
                        p.name,
                        %s,
                        'comment',
                        'VAT set to intra-community valid by default during upgrade. To ensure VIES validity, please check the VAT on the VIES website.',
                        %s
                   FROM res_partner p
                  WHERE p.vies_valid IS TRUE
        """,
        [util.ref(cr, "base.partner_root"), util.ref(cr, "mail.mt_note")],
    )
