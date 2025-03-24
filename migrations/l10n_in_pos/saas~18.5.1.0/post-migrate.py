from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    tax_tag_dict = env["account.move.line"]._get_l10n_in_tax_tag_ids()
    all_applicable_tag_ids = (
        tax_tag_dict.get("igst") + tax_tag_dict.get("cess") + tax_tag_dict.get("sgst") + tax_tag_dict.get("cgst")
    )

    # Helper to run the GSTR section update for both 'product' and 'tax' lines
    def update_gstr_section(display_type, join_table, join_condition):
        # --- ECO 9(5) --- (Need to execute first)
        query = util.format_query(
            cr,
            """
            UPDATE account_move_line aml
               SET l10n_in_gstr_section = 'sale_eco_9_5'
              FROM account_move am
              JOIN pos_session session
                ON session.move_id = am.id
              JOIN res_company company
                ON company.id = am.company_id
              JOIN res_country country
                ON country.id = company.account_fiscal_country_id,
                   account_account_tag_account_move_line_rel aml_tag_rel,
                   {join_table}
             WHERE am.move_type = 'entry'
               AND aml.move_id = am.id
               AND aml.l10n_in_gstr_section IS NULL
               AND aml.display_type = %(display_type)s
               AND country.code = 'IN'
               AND aml_tag_rel.account_account_tag_id IN %(eco_9_5)s
               AND aml_tag_rel.account_move_line_id = aml.id
               {join_condition}
            """,
            join_table=util.SQLStr(join_table),
            join_condition=util.SQLStr(join_condition),
        )
        query_mog = cr.mogrify(
            query, {"eco_9_5": tuple(tax_tag_dict.get("eco_9_5")), "display_type": display_type}
        ).decode()
        util.explode_execute(cr, query_mog, "account_move_line", alias="aml")

        cases = [
            # --- B2CS ---
            {
                "extra_join": "account_account_tag_account_move_line_rel aml_tag_rel,",
                "extra_conditions": """
                    AND aml_tag_rel.account_move_line_id = aml.id
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                """,
                "params": {
                    "gstr_section": "sale_b2cs",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- NIL RATED ---
            {
                "extra_conditions": "AND tax.l10n_in_tax_type = 'nil_rated'",
                "params": {
                    "gstr_section": "sale_nil_rated",
                    "display_type": display_type,
                },
            },
            # --- EXEMPT ---
            {
                "extra_conditions": "AND tax.l10n_in_tax_type = 'exempt'",
                "params": {
                    "gstr_section": "sale_exempt",
                    "display_type": display_type,
                },
            },
            # --- NON GST SUPPLIES ---
            {
                "extra_conditions": "AND tax.l10n_in_tax_type = 'non_gst'",
                "params": {
                    "gstr_section": "sale_non_gst_supplies",
                    "display_type": display_type,
                },
            },
        ]

        queries = []
        for case in cases:
            query = util.format_query(
                cr,
                """
                UPDATE account_move_line aml
                   SET l10n_in_gstr_section = %(gstr_section)s
                  FROM account_move am
                  JOIN pos_session session
                    ON session.move_id = am.id
                  JOIN res_company company
                    ON company.id = am.company_id
                  JOIN res_country country
                    ON country.id = company.account_fiscal_country_id,
                       {extra_join}
                       {join_table}
                 WHERE am.move_type = 'entry'
                   AND aml.move_id = am.id
                   AND aml.l10n_in_gstr_section IS NULL
                   AND aml.display_type = %(display_type)s
                   AND country.code = 'IN'
                   {join_condition}
                   {extra_conditions}
                """,
                join_table=util.SQLStr(join_table),
                extra_join=util.SQLStr(case.get("extra_join", "")),
                join_condition=util.SQLStr(join_condition),
                extra_conditions=util.SQLStr(case["extra_conditions"]),
            )
            query_mog = cr.mogrify(query, case["params"]).decode()
            queries.extend(util.explode_query_range(cr, query_mog, table="account_move_line", alias="aml"))
        util.parallel_execute(cr, queries)

    # Update for 'product' lines (join via account_move_line_account_tax_rel)
    update_gstr_section(
        "product",
        """
        account_move_line_account_tax_rel aml_tax_rel,
        account_tax tax
        """,
        """
        AND aml_tax_rel.account_move_line_id = aml.id
        AND aml_tax_rel.account_tax_id = tax.id
        """,
    )

    # Update for 'tax' lines (join via tax_line_id)
    update_gstr_section("tax", "account_tax tax", "AND aml.tax_line_id = tax.id")

    # --- Out Of Scope --- (Need to execute at the end)
    query = """
        UPDATE account_move_line aml
           SET l10n_in_gstr_section = 'sale_out_of_scope'
          FROM account_move am
          JOIN pos_session session
            ON session.move_id = am.id
          JOIN res_company company
            ON company.id = am.company_id
          JOIN res_country country
            ON country.id = company.account_fiscal_country_id
         WHERE am.move_type = 'entry'
           AND aml.move_id = am.id
           AND aml.l10n_in_gstr_section IS NULL
           AND aml.display_type IN ('product','tax')
           AND country.code = 'IN'
    """
    util.explode_execute(cr, query, "account_move_line", alias="aml")
