from odoo.upgrade import util


def migrate(cr, version):
    # deactivate taxes of IGST 0% (sale and purchase)
    cr.execute(
        """
        UPDATE account_tax t
           SET active = FALSE
          FROM ir_model_data tax_data
    CROSS JOIN res_company c
         WHERE tax_data.res_id = t.id
           AND tax_data.module = 'account'
           AND tax_data.model = 'account.tax'
           AND tax_data.name IN (c.id || '_igst_sale_0', c.id || '_igst_purchase_0')
        """
    )

    # Set LUT tax boolean for LUT taxes
    cr.execute(
        r"""
        UPDATE account_tax t
           SET l10n_in_is_lut = TRUE
          FROM ir_model_data tax_data
         WHERE tax_data.module = 'account'
           AND tax_data.model = 'account.tax'
           AND tax_data.res_id = t.id
           AND tax_data.name ~ '^\d+_igst_sale_\d+_sez_exp_lut$'
        """
    )

    tax_types = ["sgst", "cgst", "igst", "cess"]
    regular_base_tax_tags = {tax_type: util.ref(cr, f"l10n_in.tax_tag_base_{tax_type}") for tax_type in tax_types}
    regular_tax_tags = {tax_type: util.ref(cr, f"l10n_in.tax_tag_{tax_type}") for tax_type in tax_types}
    regular_rc_base_tax_tags = {tax_type: util.ref(cr, f"l10n_in.tax_tag_base_{tax_type}_rc") for tax_type in tax_types}
    regular_rc_tax_tags = {tax_type: util.ref(cr, f"l10n_in.tax_tag_{tax_type}_rc") for tax_type in tax_types}

    # Update regular gst tags in account.tax.repartition.line (purchase)
    for tax_type in tax_types:
        if tax_type == "cess":
            regex = r"^\d+_cess_21_4170_higer_purchase_rc$|^\d+_cess_purchase_\d+(_\d+)?_rc$"
        else:
            regex = rf"^\d+_{tax_type}_purchase_\d+(_\d+)?_rc$"
        cr.execute(
            """
            UPDATE account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
               SET account_account_tag_id =
                    CASE
                        WHEN rep_line.repartition_type = 'base'
                        THEN %(base_tag)s
                        WHEN rep_line.repartition_type = 'tax' AND rep_line.factor_percent = -100
                        THEN %(tax_tag)s
                     END
              FROM account_tax_repartition_line rep_line
              JOIN account_tax tax
                ON tax.id = rep_line.tax_id
              JOIN ir_model_data tax_data
                ON tax_data.res_id = rep_line.tax_id
               AND tax_data.model = 'account.tax'
             WHERE rep_line_tag_rel.account_tax_repartition_line_id = rep_line.id
               AND tax.amount_type != 'group'
               AND tax_data.module = 'account'
               AND tax_data.name ~ %(regex)s
            """,
            {
                "regex": regex,
                "base_tag": regular_base_tax_tags[tax_type],
                "tax_tag": regular_tax_tags[tax_type],
            },
        )

    # Update regular gst tags in account.tax.repartition.line (sale)
    tax_types = ["sgst", "cgst", "igst"]
    for tax_type in tax_types:
        cr.execute(
            """
            UPDATE account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
               SET account_account_tag_id = %(tax_tag)s
              FROM account_tax_repartition_line rep_line
              JOIN ir_model_data tax_data
                ON tax_data.res_id = rep_line.tax_id
               AND tax_data.model = 'account.tax'
             WHERE rep_line_tag_rel.account_tax_repartition_line_id = rep_line.id
               AND rep_line.repartition_type = 'tax'
               AND rep_line.factor_percent = -100
               AND tax_data.module = 'account'
               AND tax_data.name ~ %(regex)s
            """,
            {
                "regex": rf"^\d+_{tax_type}_sale_\d+(_\d+)?_rc$",
                "tax_tag": regular_tax_tags[tax_type],
            },
        )

    # Remove RC tags from account.tax.repartition.line (sale)
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
         WHERE rep_line_tag_rel.account_account_tag_id IN %s
        """,
        [tuple(regular_rc_base_tax_tags.values())],
    )

    # Insert regular gst tags into account.move.line (purchase)
    tax_tag_map = {
        "igst": r"^\d+_igst_purchase_\d+(_\d+)?_rc$",
        "cess": r"^\d+_cess_purchase_\d+(_\d+)?_rc$|^\d+_cess_21_4170_higer_purchase_rc$|^\d+_cess_5_plus_1591_purchase_rc$",
        "sgst": r"^\d+_sgst_purchase_\d+(_\d+)?_rc$",
        "cgst": r"^\d+_sgst_purchase_\d+(_\d+)?_rc$",
    }
    for tax_type, regex in tax_tag_map.items():
        cr.execute(
            """
            INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
                 SELECT move_line.id AS account_move_line_id,
                        %(tax_tag)s AS account_account_tag_id
                   FROM account_move_line move_line
                   JOIN account_move_line_account_tax_rel move_tax_rel
                     ON move_tax_rel.account_move_line_id = move_line.id
                   JOIN ir_model_data tax_data
                     ON tax_data.res_id = move_tax_rel.account_tax_id
                    AND tax_data.model = 'account.tax'
                  WHERE move_line.display_type = 'product'
                    AND tax_data.module = 'account'
                    AND tax_data.name ~ %(regex)s
                     ON CONFLICT DO NOTHING
            """,
            {
                "regex": regex,
                "tax_tag": regular_base_tax_tags[tax_type],
            },
        )

    # Insert regular gst tags into account.move.line
    tax_types = ["igst", "cess", "sgst", "cgst"]
    for tax_type in tax_types:
        cr.execute(
            """
            WITH tagged_lines AS (
                SELECT move_line.id AS account_move_line_id,
                       %(tax_tag)s AS account_account_tag_id
                  FROM account_move_line move_line
                  JOIN account_account_tag_account_move_line_rel rel
                    ON rel.account_move_line_id = move_line.id
                   AND rel.account_account_tag_id = %(tax_tag_rc)s
                 WHERE move_line.display_type = 'tax'
            )
            INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
                 SELECT account_move_line_id, account_account_tag_id
                   FROM tagged_lines
                     ON CONFLICT DO NOTHING
            """,
            {
                "tax_tag": regular_tax_tags[tax_type],
                "tax_tag_rc": regular_rc_tax_tags[tax_type],
            },
        )

    # Update zero rated tags in account.tax.repartition.line
    tax_tag_base_igst = util.ref(cr, "l10n_in.tax_tag_base_igst")
    tax_tag_zero_rated = util.ref(cr, "l10n_in.tax_tag_zero_rated")
    cr.execute(
        """
        UPDATE account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
           SET account_account_tag_id = %s
         WHERE rep_line_tag_rel.account_account_tag_id = %s
        """,
        [tax_tag_base_igst, tax_tag_zero_rated],
    )

    # Insert Base IGST tags into account.move.line for IGST 0% (sale and purchase)
    cr.execute(
        r"""
        INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
             SELECT move_line.id AS account_move_line_id,
                    %s AS account_account_tag_id
               FROM account_move_line move_line
               JOIN account_move_line_account_tax_rel move_tax_rel
                 ON move_tax_rel.account_move_line_id = move_line.id
               JOIN ir_model_data tax_data
                 ON tax_data.res_id = move_tax_rel.account_tax_id
                AND tax_data.model = 'account.tax'
              WHERE move_line.display_type = 'product'
                AND tax_data.module = 'account'
                AND tax_data.name ~ '^\d+_igst_(sale|purchase)_0$'
                 ON CONFLICT DO NOTHING
        """,
        [tax_tag_base_igst],
    )

    nil_tags = {
        name: util.ref(cr, f"l10n_in.{name}")
        for name in ["tax_tag_nil_rated", "tax_tag_exempt", "tax_tag_non_gst_supplies"]
    }
    # Set l10n_in_tax_type based on account.tax.repartition.line tags
    cr.execute(
        """
        UPDATE account_tax tax
           SET l10n_in_tax_type =
                CASE
                    WHEN tag_rel_line.account_account_tag_id IN %(regular_base_tags)s
                    THEN 'gst'
                    WHEN tag_rel_line.account_account_tag_id = %(nil_rated_tag)s
                    THEN 'nil_rated'
                    WHEN tag_rel_line.account_account_tag_id = %(exempt_tag)s
                    THEN 'exempt'
                    WHEN tag_rel_line.account_account_tag_id = %(non_gst_tag)s
                    THEN 'non_gst'
                 END
          FROM account_tax_repartition_line tax_rep_line
          JOIN account_account_tag_account_tax_repartition_line_rel tag_rel_line
            ON tag_rel_line.account_tax_repartition_line_id = tax_rep_line.id
         WHERE tax.id = tax_rep_line.tax_id
        """,
        {
            "regular_base_tags": (*regular_base_tax_tags.values(), tax_tag_zero_rated),
            "nil_rated_tag": nil_tags["tax_tag_nil_rated"],
            "exempt_tag": nil_tags["tax_tag_exempt"],
            "non_gst_tag": nil_tags["tax_tag_non_gst_supplies"],
        },
    )

    # Set l10n_in_tax_type for TCS
    cr.execute(
        """
        UPDATE account_tax tax
           SET l10n_in_tax_type = 'tcs'
          FROM l10n_in_section_alert section
         WHERE tax.l10n_in_section_id = section.id
           AND section.tax_source_type = 'tcs'
        """
    )

    # Set l10n_in_tax_type for TDS
    if util.column_exists(cr, "account_tax", "l10n_in_tds_tax_type"):
        cr.execute(
            """
            UPDATE account_tax tax
               SET l10n_in_tax_type = 'tds_' || l10n_in_tds_tax_type
             WHERE l10n_in_tds_tax_type IN ('sale', 'purchase')
            """
        )
        util.remove_column(cr, "account_tax", "l10n_in_tds_tax_type")

    # Remove Nil,exempt,Non-GST,zero-rated tags from account.tax.repartition.line
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
         WHERE rep_line_tag_rel.account_account_tag_id IN %s
        """,
        [(*nil_tags.values(), tax_tag_zero_rated)],
    )

    eco_tags = {
        "tax_tag_eco_tcs_52": util.ref(cr, "l10n_in.tax_tag_eco_tcs_52"),
        "tax_tag_eco_9_5": util.ref(cr, "l10n_in.tax_tag_eco_9_5"),
    }
    # Add ECO 9(5) and ECO 52 tags to account.move.line (product lines)
    query = cr.mogrify(
        """
        INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
             SELECT move_line.id AS account_move_line_id,
                    CASE industry_data.name
                        WHEN 'eco_under_section_52' THEN %(tax_tag_eco_tcs_52)s
                        ELSE %(tax_tag_eco_9_5)s
                     END
               FROM account_move_line move_line
               JOIN account_move_line_account_tax_rel move_tax_rel
                 ON move_tax_rel.account_move_line_id = move_line.id
               JOIN account_tax tax
                 ON tax.id = move_tax_rel.account_tax_id
               JOIN account_move move
                 ON move.id = move_line.move_id
               JOIN res_partner partner
                 ON partner.id = move.l10n_in_reseller_partner_id
               JOIN ir_model_data industry_data
                 ON industry_data.res_id = partner.industry_id
                AND industry_data.model = 'res.partner.industry'
              WHERE {parallel_filter}
                AND move_line.display_type = 'product'
                AND tax.l10n_in_tax_type IN ('gst', 'nil_rated', 'exempt', 'non_gst')
                AND industry_data.module = 'l10n_in'
                AND industry_data.name IN ('eco_under_section_52', 'eco_under_section_9_5')
                 ON CONFLICT DO NOTHING
        """,
        {
            "tax_tag_eco_tcs_52": eco_tags["tax_tag_eco_tcs_52"],
            "tax_tag_eco_9_5": eco_tags["tax_tag_eco_9_5"],
        },
    ).decode()
    util.explode_execute(cr, query, "account_move_line", alias="move_line")

    # Add ECO 9(5) and ECO 52 tags to account.move.line (tax lines)
    query = cr.mogrify(
        """
        INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
             SELECT move_line.id,
                    CASE industry_data.name
                        WHEN 'eco_under_section_52' THEN %(tax_tag_eco_tcs_52)s
                        ELSE %(tax_tag_eco_9_5)s
                     END AS account_account_tag_id
               FROM account_move_line move_line
               JOIN account_tax tax
                 ON tax.id = move_line.tax_line_id
               JOIN account_move move
                 ON move.id = move_line.move_id
               JOIN res_partner partner
                 ON partner.id = move.l10n_in_reseller_partner_id
               JOIN ir_model_data industry_data
                 ON industry_data.res_id = partner.industry_id
                AND industry_data.model = 'res.partner.industry'
               JOIN account_account_tag_account_move_line_rel rel2
                 ON rel2.account_move_line_id = move_line.id
              WHERE {parallel_filter}
                AND move_line.display_type = 'tax'
                AND tax.l10n_in_tax_type IN ('gst', 'nil_rated', 'exempt', 'non_gst')
                AND industry_data.module = 'l10n_in'
                AND industry_data.name IN ('eco_under_section_52', 'eco_under_section_9_5')
                 ON CONFLICT DO NOTHING
        """,
        {
            "tax_tag_eco_tcs_52": eco_tags["tax_tag_eco_tcs_52"],
            "tax_tag_eco_9_5": eco_tags["tax_tag_eco_9_5"],
        },
    ).decode()
    util.explode_execute(cr, query, "account_move_line", alias="move_line")

    tax_types = ["sgst", "cgst", "igst", "cess"]
    non_itc_gst_tags = {tax_type: util.ref(cr, f"l10n_in.tax_tag_non_itc_{tax_type}") for tax_type in tax_types}
    other_non_itc_gst_tags = {
        tax_type: util.ref(cr, f"l10n_in.tax_tag_other_non_itc_{tax_type}") for tax_type in tax_types
    }
    non_itc_tag = util.ref(cr, "l10n_in.tax_tag_non_itc")
    other_non_itc_tag = util.ref(cr, "l10n_in.tax_tag_other_non_itc")

    for tax_type in tax_types:
        # Insert Non ITC tag and GST tag into account.tax.repartition.line
        cr.execute(
            """
            INSERT INTO account_account_tag_account_tax_repartition_line_rel (
                        account_tax_repartition_line_id, account_account_tag_id)
                 SELECT tag_rel.account_tax_repartition_line_id AS rep_line_id,
                        UNNEST(%(tags)s)
                   FROM account_account_tag_account_tax_repartition_line_rel tag_rel
                  WHERE tag_rel.account_account_tag_id = %(non_itc_gst_tags)s
                     ON CONFLICT DO NOTHING
            """,
            {
                "tags": [regular_tax_tags[tax_type], non_itc_tag],
                "non_itc_gst_tags": non_itc_gst_tags[tax_type],
            },
        )

        # Insert Other Non ITC tag and GST tag into account.tax.repartition.line
        cr.execute(
            """
            INSERT INTO account_account_tag_account_tax_repartition_line_rel (
                        account_tax_repartition_line_id, account_account_tag_id)
                 SELECT tag_rel.account_tax_repartition_line_id,
                        UNNEST(%(tags)s)
                   FROM account_account_tag_account_tax_repartition_line_rel tag_rel
                  WHERE tag_rel.account_account_tag_id = %(other_non_itc_gst_tags)s
                     ON CONFLICT DO NOTHING
            """,
            {
                "tags": [regular_tax_tags[tax_type], other_non_itc_tag],
                "other_non_itc_gst_tags": other_non_itc_gst_tags[tax_type],
            },
        )

        # Insert Non ITC and GST tags into account.move.line
        cr.execute(
            """
            INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
                 SELECT tag_rel.account_move_line_id,
                        UNNEST(%(tags)s)
                   FROM account_account_tag_account_move_line_rel tag_rel
                  WHERE tag_rel.account_account_tag_id = %(non_itc_gst_tags)s
                     ON CONFLICT DO NOTHING
            """,
            {
                "tags": [regular_tax_tags[tax_type], non_itc_tag],
                "non_itc_gst_tags": non_itc_gst_tags[tax_type],
            },
        )

        # Insert Other Non ITC and GST tags into account.move.line
        cr.execute(
            """
            INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id)
                 SELECT tag_rel.account_move_line_id,
                        UNNEST(%(tags)s)
                   FROM account_account_tag_account_move_line_rel tag_rel
                  WHERE tag_rel.account_account_tag_id = %(other_non_itc_gst_tags)s
                     ON CONFLICT DO NOTHING
            """,
            {
                "tags": [regular_tax_tags[tax_type], other_non_itc_tag],
                "other_non_itc_gst_tags": other_non_itc_gst_tags[tax_type],
            },
        )

    # Remove Non ITC and Other non ITC tags of SGST,CGST,IGST and CESS from account.tax.repartition.line
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
         WHERE account_account_tag_id IN %s
        """,
        [tuple(non_itc_gst_tags.values()) + tuple(other_non_itc_gst_tags.values())],
    )

    # Apply gstr section to account.move.line
    env = util.env(cr)
    tax_tag_dict = env["account.move.line"]._get_l10n_in_tax_tag_ids()
    all_applicable_tag_ids = (
        tax_tag_dict.get("igst") + tax_tag_dict.get("cess") + tax_tag_dict.get("sgst") + tax_tag_dict.get("cgst")
    )

    # Helper to run the GSTR section update for both 'product' and 'tax' lines
    def update_gstr_section(display_type, join_table, join_condition):
        # --- SALE: ECO 9(5) --- (Need to execute first)
        query = util.format_query(
            cr,
            """
            UPDATE account_move_line aml
               SET l10n_in_gstr_section = 'sale_eco_9_5'
              FROM account_move am
              JOIN res_company company
                ON company.id = am.company_id
              JOIN res_country country
                ON country.id = company.account_fiscal_country_id,
                   account_account_tag_account_move_line_rel aml_tag_rel,
                   {join_table}
             WHERE am.move_type IN ('out_invoice', 'out_receipt', 'out_refund')
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
            # --- SALE: B2B RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_b2b_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- SALE: B2B REGULAR ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_b2b_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNR RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnr_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNR REGULAR ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnr_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- SALE: SEZ WP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'special_economic_zone'
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN  %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_sez_wp",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: SEZ WOP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'special_economic_zone'
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN  %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS TRUE
                """,
                "params": {
                    "gstr_section": "sale_sez_wop",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNR SEZ WP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'special_economic_zone'
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnr_sez_wp",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNR SEZ WOP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'special_economic_zone'
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnr_sez_wop",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: EXP WP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN  %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_exp_wp",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: EXP WOP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN  %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS TRUE
                """,
                "params": {
                    "gstr_section": "sale_exp_wop",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNUR EXP WP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnur_exp_wp",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNUR EXP WOP ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnur_exp_wop",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- SALE: DEEMED EXPORT ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'deemed_export'
                    AND am.move_type IN ('out_invoice', 'out_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN  %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS TRUE
                """,
                "params": {
                    "gstr_section": "sale_deemed_export",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- SALE: CDNR DEEMED EXPORT ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND (   am.move_type = 'out_refund'
                         OR (    am.move_type = 'out_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                    AND tax.l10n_in_is_lut IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "sale_cdnr_deemed_export",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: B2B RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                """,
                "params": {
                    "gstr_section": "purchase_b2b_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: B2B REGULAR ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND (
                        (am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders', 'deemed_export') AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s)
                        OR
                        (am.l10n_in_gst_treatment = 'special_economic_zone' AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s)
                    )
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_b2b_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: CDNR RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders')
                    AND (   am.move_type = 'in_refund'
                         OR (    am.move_type = 'in_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                """,
                "params": {
                    "gstr_section": "purchase_cdnr_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: CDNR REGULAR ---
            {
                "extra_conditions": """
                    AND (   am.move_type = 'in_refund'
                         OR (    am.move_type = 'in_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND (
                        (am.l10n_in_gst_treatment IN ('regular', 'composition', 'uin_holders', 'deemed_export') AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s)
                        OR
                        (am.l10n_in_gst_treatment = 'special_economic_zone' AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s)
                    )
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_cdnr_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: B2C RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('unregistered', 'consumer')
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                """,
                "params": {
                    "gstr_section": "purchase_b2c_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: B2C REGULAR ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('unregistered', 'consumer')
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_b2c_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: CDNUR RCM ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('unregistered', 'consumer')
                    AND (   am.move_type = 'in_refund'
                         OR (    am.move_type = 'in_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS TRUE
                """,
                "params": {
                    "gstr_section": "purchase_cdnur_rcm",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: CDNUR REGULAR ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment IN ('unregistered', 'consumer')
                    AND (   am.move_type = 'in_refund'
                         OR (    am.move_type = 'in_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(all_applicable_tag_ids)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_cdnur_regular",
                    "all_applicable_tag_ids": tuple(all_applicable_tag_ids),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: OVERSEAS CDNUR REGULAR ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND (   am.move_type = 'in_refund'
                         OR (    am.move_type = 'in_invoice'
                             AND am.debit_origin_id IS NOT NULL
                            )
                        )
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_cdnur_regular",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: IMP SERVICES ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.tax_scope = 'service'
                """,
                "params": {
                    "gstr_section": "purchase_imp_services",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: IMP GOODS ---
            {
                "extra_conditions": """
                    AND am.l10n_in_gst_treatment = 'overseas'
                    AND am.move_type IN ('in_invoice', 'in_receipt')
                    AND am.debit_origin_id IS NULL
                    AND aml_tag_rel.account_account_tag_id IN %(igst_cess)s
                    AND tax.l10n_in_reverse_charge IS NOT TRUE
                """,
                "params": {
                    "gstr_section": "purchase_imp_goods",
                    "igst_cess": tuple(tax_tag_dict.get("igst") + tax_tag_dict.get("cess")),
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
                  JOIN res_company company
                    ON company.id = am.company_id
                  JOIN res_country country
                    ON country.id = company.account_fiscal_country_id,
                       account_account_tag_account_move_line_rel aml_tag_rel,
                       {join_table}
                 WHERE {{parallel_filter}}
                   AND aml.move_id = am.id
                   AND aml.l10n_in_gstr_section IS NULL
                   AND aml.display_type = %(display_type)s
                   AND country.code = 'IN'
                   AND aml_tag_rel.account_move_line_id = aml.id
                   {join_condition}
                   {extra_conditions}
                """,
                join_table=util.SQLStr(join_table),
                join_condition=util.SQLStr(join_condition),
                extra_conditions=util.SQLStr(case["extra_conditions"]),
            )
            query_mog = cr.mogrify(query, case["params"]).decode()
            queries.extend(util.explode_query_range(cr, query_mog, table="account_move_line", alias="aml"))

        nil_cases = [
            # --- SALE: NIL RATED ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('out_invoice', 'out_receipt', 'out_refund')
                    AND tax.l10n_in_tax_type = 'nil_rated'
                """,
                "params": {
                    "gstr_section": "sale_nil_rated",
                    "display_type": display_type,
                },
            },
            # --- SALE: EXEMPT ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('out_invoice', 'out_receipt', 'out_refund')
                    AND tax.l10n_in_tax_type = 'exempt'
                """,
                "params": {
                    "gstr_section": "sale_exempt",
                    "display_type": display_type,
                },
            },
            # --- SALE: NON GST SUPPLIES ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('out_invoice', 'out_receipt', 'out_refund')
                    AND tax.l10n_in_tax_type = 'non_gst'
                """,
                "params": {
                    "gstr_section": "sale_non_gst_supplies",
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: NIL RATED ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('in_invoice', 'in_receipt', 'in_refund')
                    AND tax.l10n_in_tax_type = 'nil_rated'
                """,
                "params": {
                    "gstr_section": "purchase_nil_rated",
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: EXEMPT ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('in_invoice', 'in_receipt', 'in_refund')
                    AND tax.l10n_in_tax_type = 'exempt'
                """,
                "params": {
                    "gstr_section": "purchase_exempt",
                    "display_type": display_type,
                },
            },
            # --- PURCHASE: NON GST SUPPLIES ---
            {
                "extra_conditions": """
                    AND am.move_type IN ('in_invoice', 'in_receipt', 'in_refund')
                    AND tax.l10n_in_tax_type = 'non_gst'
                """,
                "params": {
                    "gstr_section": "purchase_non_gst_supplies",
                    "display_type": display_type,
                },
            },
        ]
        for case in nil_cases:
            query = util.format_query(
                cr,
                """
                UPDATE account_move_line aml
                   SET l10n_in_gstr_section = %(gstr_section)s
                  FROM account_move am
                  JOIN res_company company
                    ON company.id = am.company_id
                  JOIN res_country country
                    ON country.id = company.account_fiscal_country_id,
                       {join_table}
                 WHERE aml.move_id = am.id
                   AND aml.l10n_in_gstr_section IS NULL
                   AND aml.display_type = %(display_type)s
                   AND am.l10n_in_gst_treatment != 'overseas'
                   AND country.code = 'IN'
                   {join_condition}
                   {extra_conditions}
                """,
                join_table=util.SQLStr(join_table),
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

    cr.execute(
        """
        SELECT aml.id
          FROM account_move_line aml
          JOIN account_move am
            ON am.id = aml.move_id
          JOIN res_company company
            ON company.id = am.company_id
          JOIN res_country country
            ON country.id = company.account_fiscal_country_id
         WHERE aml.display_type IN ('product','tax')
           AND aml.l10n_in_gstr_section IS NULL
           AND am.move_type != 'entry'
           AND country.code = 'IN'
        """
    )
    line_ids = [lineid for (lineid,) in cr.fetchall()]

    # For complicated cases like sale_b2cs, sale_cdnur_b2cl
    if line_ids:
        util.iter_browse(env["account.move.line"], line_ids)._set_l10n_in_gstr_section()
