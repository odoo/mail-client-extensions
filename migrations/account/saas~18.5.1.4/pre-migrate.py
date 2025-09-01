from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="res.partner", fieldname="duplicated_bank_account_partners_count")
    util.remove_field(cr, model="res.company", fieldname="account_sale_receipt_tax_id")
    util.remove_field(cr, model="res.company", fieldname="account_purchase_receipt_tax_id")
    util.remove_field(cr, "account.tax", "name_searchable")
    util.move_field_to_module(cr, "account.move", "taxable_supply_date", "l10n_cz", "account")
    util.move_field_to_module(cr, "account.move", "taxable_supply_date", "l10n_sk", "account")
    util.move_field_to_module(cr, "account.move", "taxable_supply_date", "l10n_pl", "account")

    util.create_column(cr, "account_move_line", "no_followup", "bool")
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET no_followup = True
          FROM account_move m
         WHERE l.move_id = m.id
           AND m.move_type = 'entry'
           AND m.origin_payment_id IS NULL
        """,
        table="account_move_line",
        alias="l",
    )
    util.remove_field(cr, "res.config.settings", "module_l10n_eu_oss")

    cr.execute(
        """
        UPDATE res_company
           SET account_storno = true
          FROM res_country
         WHERE res_country.id = res_company.account_fiscal_country_id
           AND res_country.code IN ('BA', 'CN', 'CZ', 'HR', 'PL', 'RO', 'RS', 'RU', 'SI', 'SK', 'UA')
        """,
    )

    util.create_column(cr, "account_move_line", "is_storno", "boolean")
    query = """
        UPDATE account_move_line AS aml
           SET is_storno = true
          FROM account_move AS am
         WHERE aml.move_id = am.id
           AND am.is_storno
        """
    util.explode_execute(cr, query, table="account_move_line", alias="aml")

    util.make_field_non_stored(cr, "account.move", "is_storno", selectable=False)

    # Update Greek companies first due to a special case, see commit message
    greece_country_id = util.ref(cr, "base.gr")
    cr.execute(
        """
        WITH _pairs_of_fps_of_greek_companies AS (
            SELECT ARRAY_AGG(fp.id ORDER BY fp.sequence, fp.id) AS fp_ids
              FROM account_fiscal_position fp
              JOIN res_company c
                ON c.id = fp.company_id
              JOIN res_partner p
                ON p.id = c.partner_id
               AND p.country_id = %s
             GROUP BY fp.company_id
        )
        UPDATE account_fiscal_position fp1
           SET zip_from = '10',
               zip_to = '69'
          FROM _pairs_of_fps_of_greek_companies cte
          JOIN account_fiscal_position fp2
            ON fp2.id = cte.fp_ids[2]
         WHERE cte.fp_ids[1] = fp1.id
           AND fp1.zip_from IS NULL
           AND fp1.zip_to IS NULL
           AND fp2.zip_from = '70'
           AND fp2.zip_to = '85'
           AND fp1.country_id = fp2.country_id
           AND fp1.country_id = %s
        """,
        [greece_country_id, greece_country_id],
    )

    cr.execute("""
        WITH _new_sequences AS (
            SELECT fp.id AS fp_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY fp.company_id
                           ORDER BY fp.vat_required IS TRUE DESC,
                                    fp.zip_from IS NOT NULL DESC,
                                    fp_state.account_fiscal_position_id IS NOT NULL DESC,
                                    fp.country_id IS NOT NULL DESC,
                                    fp.country_group_id IS NOT NULL DESC,
                                    COALESCE(fp.sequence, 0),
                                    fp.id
                   ) AS value
              FROM account_fiscal_position fp
         LEFT JOIN account_fiscal_position_res_country_state_rel fp_state
                ON fp_state.account_fiscal_position_id = fp.id
             WHERE fp.auto_apply
        )
        UPDATE account_fiscal_position fp
           SET sequence = ns.value
          FROM _new_sequences ns
         WHERE fp.id = ns.fp_id
    """)
