import re

from odoo.upgrade import util

# The tax report was wrong, we need to add lines in a new journal to keep it unchanged
TAGS_TO_INVERT = [
    # BE
    ("attn_VAT-IN-V82-21-EU-G-D35-ALRD-IN-BE", "invoice", "+56"),
    # BF
    ("tva_sale_self_18", "refund", "-BF_20"),  # TODO double check BF
    # BR
    ("tax_template_in_icms_externo7", "invoice", "+ICMS_1"),
    ("tax_template_in_icms_externo7", "invoice", "+ICMS_2"),
    ("tax_template_in_icms_externo7", "refund", "-ICMS_1"),
    ("tax_template_in_icms_externo7", "refund", "-ICMS_2"),
    ("tax_template_in_icms_externo12", "invoice", "+ICMS_1"),
    ("tax_template_in_icms_externo12", "invoice", "+ICMS_2"),
    ("tax_template_in_icms_externo12", "refund", "-ICMS_1"),
    ("tax_template_in_icms_externo12", "refund", "-ICMS_2"),
    ("tax_template_in_ii0", "invoice", "+II_1"),
    ("tax_template_in_ii0", "refund", "-II_1"),
    ("tax_template_in_inss0", "invoice", "+INSS_1"),
    ("tax_template_in_inss0", "refund", "-INSS_1"),
    # DE
    ("tax_ust_free_mobil_skr03", "invoice", "-60"),
    ("tax_ust_free_mobil_skr03", "refund", "+60"),
    ("tax_ust_19_13b_eu_ohne_vst_skr03", "invoice", "+47"),
    ("tax_ust_19_13b_eu_ohne_vst_skr03", "refund", "-47"),
    ("tax_ust_7_13b_eu_ohne_vst_skr03", "invoice", "+47"),
    ("tax_ust_7_13b_eu_ohne_vst_skr03", "refund", "-47"),
    # see PR #7156
    ("account_tax_template_purchase_eu_0_code071", "invoice", "-KZ 070"),
    ("account_tax_template_purchase_eu_0_code071", "invoice", "-KZ 071"),
    ("account_tax_template_purchase_eu_0_code071", "refund", "+KZ 070"),
    ("account_tax_template_purchase_eu_0_code071", "refund", "+KZ 071"),
    ("account_tax_template_purchase_eu_20", "invoice", "-KZ 070"),
    ("account_tax_template_purchase_eu_20", "invoice", "-KZ 072"),
    ("account_tax_template_purchase_eu_20", "refund", "+KZ 070"),
    ("account_tax_template_purchase_eu_20", "refund", "+KZ 072"),
    ("account_tax_template_purchase_eu_10", "invoice", "-KZ 070"),
    ("account_tax_template_purchase_eu_10", "invoice", "-KZ 073"),
    ("account_tax_template_purchase_eu_10", "refund", "+KZ 070"),
    ("account_tax_template_purchase_eu_10", "refund", "+KZ 073"),
    ("account_tax_template_purchase_eu_13", "invoice", "-KZ 070"),
    ("account_tax_template_purchase_eu_13", "invoice", "-KZ 008"),
    ("account_tax_template_purchase_eu_13", "refund", "+KZ 070"),
    ("account_tax_template_purchase_eu_13", "refund", "+KZ 008"),
    ("account_tax_template_purchase_eu_19", "invoice", "-KZ 070"),
    ("account_tax_template_purchase_eu_19", "invoice", "-KZ 088"),
    ("account_tax_template_purchase_eu_19", "refund", "+KZ 070"),
    ("account_tax_template_purchase_eu_19", "refund", "+KZ 088"),
    ("account_tax_template_purchase_eu_xx_code076", "invoice", "-KZ 076"),
    ("account_tax_template_purchase_eu_xx_code076", "invoice", "-KZ 077"),
    ("account_tax_template_purchase_eu_xx_code076", "refund", "+KZ 076"),
    ("account_tax_template_purchase_eu_xx_code076", "refund", "+KZ 077"),
    ("account_tax_template_purchase_eu_xx_vst_076", "invoice", "-KZ 076"),
    ("account_tax_template_purchase_eu_xx_vst_076", "invoice", "-KZ 077"),
    ("account_tax_template_purchase_eu_xx_vst_076", "refund", "+KZ 076"),
    ("account_tax_template_purchase_eu_xx_vst_076", "refund", "+KZ 077"),
]

# The tax report was correct but with the wrong sign on a line with the wrong line (-1 * -1 = 1)
# We need to switch the tag on a line with the opposite sign
TAGS_TO_SWITCH = [
    # BF
    ("tva_sale_self_18", "invoice", "+BF_20", 100, -100),
    ("tva_sale_self_18", "invoice", "-BF_15_tax", -100, 100),
    # BH
    ("l10n_bh_purchase_10_RC_D", "invoice", "-12 T", 100, -100),
    ("l10n_bh_purchase_10_RC_D", "refund", "+12 T", 100, -100),
    ("l10n_bh_purchase_10_RC", "invoice", "-11(a) T", 100, -100),
    ("l10n_bh_purchase_10_RC", "refund", "+11(a) T", 100, -100),
    # CY
    ("VAT_P_IN_EU_19_S_ESSS", "invoice", "+1", 100, -100),
    ("VAT_P_IN_EU_19_S_ESSS", "refund", "-1", 100, -100),
    # CZ
    ("l10n_cz_12_purchase_goods_eu", "invoice", "-VAT 4 Tax", -100, 100),
    ("l10n_cz_21_acquisition_goods_eu", "invoice", "-VAT 3 Tax", -100, 100),
    ("l10n_cz_12_receipt_service_person_eu", "invoice", "-VAT 6 Tax", -100, 100),
    ("l10n_cz_21_receipt_service_person_eu", "invoice", "-VAT 5 Tax", -100, 100),
    ("l10n_cz_21_receipt_service_person_non_eu", "invoice", "-VAT 12 Tax", -100, 100),
    ("l10n_cz_21_tax_reverse_charge_scheme", "invoice", "-VAT 10 Tax", -100, 100),
    ("l10n_cz_21_other_supplies_chargeable", "invoice", "-VAT 12 Tax", -100, 100),
    ("l10n_cz_12_other_supplies_obligation", "invoice", "-VAT 13 Tax", -100, 100),
    ("l10n_cz_12_tax_reverse_charge_scheme", "invoice", "-VAT 11 Tax", -100, 100),
    # DE
    ("tax_ust_vst_19_purchase_13b_bau_skr03", "invoice", "-85", -100, 100),
    ("tax_ust_vst_19_purchase_13b_bau_skr03", "refund", "+85", -100, 100),
    ("tax_ust_vst_7_purchase_13b_bau_skr03", "invoice", "-85", -100, 100),
    ("tax_ust_vst_7_purchase_13b_bau_skr03", "refund", "+85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_mobil_skr03", "invoice", "-85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_mobil_skr03", "refund", "+85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_werk_ausland_skr03", "invoice", "-85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_werk_ausland_skr03", "refund", "+85", -100, 100),
    ("tax_vst_ust_7_purchase_13b_werk_ausland_skr03", "invoice", "-85", -100, 100),
    ("tax_vst_ust_7_purchase_13b_werk_ausland_skr03", "refund", "+85", -100, 100),
    ("tax_ust_vst_19_purchase_13b_bau_skr04", "invoice", "-85", -100, 100),
    ("tax_ust_vst_19_purchase_13b_bau_skr04", "refund", "+85", -100, 100),
    ("tax_ust_vst_7_purchase_13b_bau_skr04", "invoice", "-85", -100, 100),
    ("tax_ust_vst_7_purchase_13b_bau_skr04", "refund", "+85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_mobil_skr04", "invoice", "-85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_mobil_skr04", "refund", "+85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_werk_ausland_skr04", "invoice", "-85", -100, 100),
    ("tax_vst_ust_19_purchase_13b_werk_ausland_skr04", "refund", "+85", -100, 100),
    ("tax_vst_ust_7_purchase_13b_werk_ausland_skr04", "invoice", "-85", -100, 100),
    ("tax_vst_ust_7_purchase_13b_werk_ausland_skr04", "refund", "+85", -100, 100),
    # DK
    ("tax_kdk01", "refund", "-UM", 100, -100),
    ("tax_kdk01", "refund", "+KM", -100, 100),
    ("tax_kdk02", "refund", "-UM", 100, -100),
    ("tax_kdk02", "refund", "+KM", -100, 100),
    ("tax_kdk03", "refund", "-UM", 100, -100),
    ("tax_kdk03", "refund", "+KM", -100, 100),
    ("tax_kdk00", "refund", "-UM", 100, -100),
    ("tax_kdk00", "refund", "+KM", -100, 100),
    ("tax_kdk04", "refund", "-UM", 100, -100),
    ("tax_kdk04", "refund", "+KM", -100, 100),
    ("tax_k%euv1", "invoice", "+MVU", 100, -100),
    ("tax_k%euv1", "invoice", "-KM", -100, 100),
    ("tax_k%euv1", "refund", "-MVU", 100, -100),
    ("tax_k%euv1", "refund", "+KM", -100, 100),
    ("tax_k%euv3", "invoice", "+MVU", 100, -100),
    ("tax_k%euv3", "invoice", "-KM", -100, 100),
    ("tax_k%euv3", "refund", "-MVU", 100, -100),
    ("tax_k%euv3", "refund", "+KM", -100, 100),
    ("tax_k%euv4", "invoice", "+MVU", 100, -100),
    ("tax_k%euv4", "invoice", "-KM", -100, 100),
    ("tax_k%euv4", "refund", "-MVU", 100, -100),
    ("tax_k%euv4", "refund", "+KM", -100, 100),
]

# A new tag has been added in order to increase both on debit and credit
REVERSE_CHARGE_TAGS = [
    ("tax_ust_vst_19_purchase_13b_bau_skr03", "60", "60rc"),
    ("tax_ust_vst_7_purchase_13b_bau_skr03", "60", "60rc"),
    ("tax_vst_ust_19_purchase_13b_mobil_skr03", "60", "60rc"),
]


def update_m2m_tag_rel(cr, m2m_table):
    cr.execute(
        util.format_query(
            cr,
            """
            UPDATE {m2m_table} rel
               SET account_account_tag_id = _upg_tag_pairs.plus_tag_id
              FROM _upg_tag_pairs
             WHERE rel.account_account_tag_id = _upg_tag_pairs.minus_tag_id
            """,
            m2m_table=m2m_table,
        )
    )


def migrate(cr, version):
    util.remove_field(cr, "account.move.line", "tax_tag_invert")
    util.remove_field(cr, "account.account.tag", "tax_negate")

    cr.execute(
      """
        SELECT minus_tag.id AS minus_tag_id,
               plus_tag.id AS plus_tag_id
          INTO UNLOGGED TABLE _upg_tag_pairs
          FROM account_account_tag minus_tag,
               account_account_tag plus_tag
         WHERE SUBSTRING(minus_tag.name->>'en_US' FROM 2) = SUBSTRING(plus_tag.name->>'en_US' FROM 2)
           AND minus_tag.country_id = plus_tag.country_id
           AND SUBSTRING(minus_tag.name->>'en_US' FOR 1) = '-'
           AND SUBSTRING(plus_tag.name->>'en_US' FOR 1) = '+'
           AND minus_tag.applicability = 'taxes'
           AND plus_tag.applicability = 'taxes'
      """
    )

    # Save errors from the past in a temp table in order to recreate them in the post script
    # query for tax lines
    cr.execute_values(
        """
        SELECT aml.company_id,
               aml.date,
               aml.account_id,
               tag.id AS tag_id,
               SUM(aml.balance) AS balance
          INTO UNLOGGED TABLE _upg_to_create_aml
          FROM (VALUES %s) AS faulty_data(xmlid_re, document_type, tag),
               account_move_line aml
          JOIN account_tax_repartition_line repartition
            ON repartition.id = aml.tax_repartition_line_id
          JOIN account_account_tag_account_tax_repartition_line_rel tag_rel
            ON tag_rel.account_tax_repartition_line_id = repartition.id
          JOIN account_account_tag tag
            ON tag_rel.account_account_tag_id = tag.id
          JOIN ir_model_data tax_imd
            ON tax_imd.res_id = repartition.tax_id
           AND tax_imd.model = 'account.tax'
           AND tax_imd.module = 'account'
         WHERE tax_imd.name ~ faulty_data.xmlid_re
           AND tag.name->>'en_US' = faulty_data.tag
           AND repartition.document_type = faulty_data.document_type
      GROUP BY aml.company_id, aml.date, aml.account_id, tag.id
        """,
        [
            (rf"^\d+_{re.escape(xmlid)}$", document_type, tag)
            for xmlid, document_type, tag in TAGS_TO_INVERT
        ],
    )
    # query for base lines
    cr.execute_values(
        """
   INSERT INTO _upg_to_create_aml
        SELECT aml.company_id,
               aml.date,
               aml.account_id,
               tag.id AS tag_id,
               SUM(aml.balance) AS balance
          FROM (VALUES %s) AS faulty_data(xmlid_re, document_type, tag),
               account_move_line aml
          JOIN account_move move
            ON move.id = aml.move_id
          JOIN account_move_line_account_tax_rel tax_rel
            ON tax_rel.account_move_line_id = aml.id
          JOIN account_tax_repartition_line repartition
            ON repartition.tax_id = tax_rel.account_tax_id
           AND repartition.repartition_type = 'base'
           AND repartition.document_type = CASE WHEN move.move_type LIKE '%%refund' THEN 'refund' ELSE 'invoice' END
          JOIN account_account_tag_account_tax_repartition_line_rel tag_rel
            ON tag_rel.account_tax_repartition_line_id = repartition.id
          JOIN account_account_tag tag
            ON tag_rel.account_account_tag_id = tag.id
          JOIN ir_model_data tax_imd
            ON tax_imd.res_id = repartition.tax_id
           AND tax_imd.model = 'account.tax'
           AND tax_imd.module = 'account'
         WHERE tax_imd.name ~ faulty_data.xmlid_re
           AND tag.name->>'en_US' = faulty_data.tag
           AND repartition.document_type = faulty_data.document_type
      GROUP BY aml.company_id, aml.date, aml.account_id, tag.id
        """,
        [
            (rf"^\d+_{re.escape(xmlid)}$", document_type, tag)
            for xmlid, document_type, tag in TAGS_TO_INVERT
        ],
    )

    # The report was correct but the tag was set with the wrong sign on a line with the wrong balance sign: -1 * -1 = 1
    # We are just moving the tag to the correct line. The target sign doesn't matter since it will be changed to + just after
    cr.execute_values(
        """
        UPDATE account_account_tag_account_move_line_rel tag_aml_rel
           SET account_move_line_id = target_line.id
          FROM (VALUES %s) AS faulty_data(xmlid_re, document_type, tag, source_factor, target_factor),
               account_move_line source_line
          JOIN account_tax_repartition_line source_repartition
            ON source_repartition.id = source_line.tax_repartition_line_id
          JOIN account_account_tag_account_tax_repartition_line_rel source_tag_rel
            ON source_tag_rel.account_tax_repartition_line_id = source_repartition.id
          JOIN account_account_tag source_tag
            ON source_tag_rel.account_account_tag_id = source_tag.id
          JOIN ir_model_data tax_imd
            ON tax_imd.res_id = source_repartition.tax_id
           AND tax_imd.model = 'account.tax'
           AND tax_imd.module = 'account',
               account_move_line target_line
          JOIN account_tax_repartition_line target_repartition
            ON target_repartition.id = target_line.tax_repartition_line_id
         WHERE tag_aml_rel.account_move_line_id = source_line.id
           AND tag_aml_rel.account_account_tag_id = source_tag.id
           AND source_line.move_id = target_line.move_id
           AND source_repartition.tax_id = target_repartition.tax_id
           AND source_repartition.repartition_type = target_repartition.repartition_type
           AND tax_imd.name ~ faulty_data.xmlid_re
           AND source_repartition.document_type = faulty_data.document_type
           AND target_repartition.document_type = faulty_data.document_type
           AND source_repartition.factor_percent = faulty_data.source_factor
           AND target_repartition.factor_percent = faulty_data.target_factor
           AND source_tag.name ->> 'en_US' = faulty_data.tag
        """,
        [
            (rf"^\d+_{re.escape(xmlid)}$", document_type, tag, source_factor, target_factor)
            for xmlid, document_type, tag, source_factor, target_factor in TAGS_TO_SWITCH
        ],
    )

    update_m2m_tag_rel(cr, "account_account_tag_account_move_line_rel")
