from odoo.upgrade import util

DEACTIVATE_TAXES = (
    "au_tax_sale_inc_10",
    "au_tax_purchase_inc_10_service",
    "au_tax_purchase_inc_10_service_tpar",
    "au_tax_purchase_inc_10_service_tpar_no_abn",
    "tax_template_out_aproxtrib_fed_incl_goods",
    "tax_template_out_aproxtrib_state_incl_goods",
    "tax_template_out_cofins_incl_goods",
    "tax_template_out_cofins_deson_incl_goods",
    "tax_template_out_cofins_st_incl_goods",
    "tax_template_out_icms_incl_goods",
    "tax_template_out_icms_credsn_incl_goods",
    "tax_template_out_icms_deson_incl_goods",
    "tax_template_out_icms_difa_dest_incl_goods",
    "tax_template_out_icms_difa_fcp_incl_goods",
    "tax_template_out_icms_difa_remet_incl_goods",
    "tax_template_out_icms_eff_incl_goods",
    "tax_template_out_icms_fcp_incl_goods",
    "tax_template_out_icms_own_payer_incl_goods",
    "tax_template_out_icms_part_incl_goods",
    "tax_template_out_icms_rf_incl_goods",
    "tax_template_out_icms_st_incl_goods",
    "tax_template_out_icms_st_fcp_incl_goods",
    "tax_template_out_icms_st_fcppart_incl_goods",
    "tax_template_out_icms_st_part_incl_goods",
    "tax_template_out_icms_st_sd_incl_goods",
    "tax_template_out_icms_st_sd_fcp_incl_goods",
    "tax_template_out_ii_incl_goods",
    "tax_template_out_iof_incl_goods",
    "tax_template_out_ipi_incl_goods",
    "tax_template_out_ipi_returned_incl_goods",
    "tax_template_out_pis_incl_goods",
    "tax_template_out_pis_deson_incl_goods",
    "tax_template_out_pis_st_incl_goods",
    "tax_template_out_aproxtrib_city_incl_service",
    "tax_template_out_pis_rf_incl_service",
    "tax_template_out_cofins_rf_incl_service",
    "tax_template_out_csll_incl_service",
    "tax_template_out_csll_rf_incl_service",
    "tax_template_out_iss_incl_service",
    "tax_template_out_iss_rf_incl_service",
    "tax_template_out_ir_pj_incl_service",
    "tax_template_out_ir_rf_incl_service",
    "tax_template_out_cprb_incl_service",
    "tax_template_out_cprb_rf_incl_service",
    "tax_template_out_inss_ar_incl_service",
    "tax_template_out_inss_rf_incl_service",
    "vat_25_incl",
    "vat_25_purchase_incl",
    "vat_25_invest_incl",
    "vat_37_incl",
    "vat_37_purchase_incl",
    "vat_37_invest_incl",
    "vat_77_incl",
    "vat_77_purchase_incl",
    "vat_77_invest_incl",
    "vat_sale_26_incl",
    "vat_purchase_26_incl",
    "vat_purchase_26_invest_incl",
    "vat_sale_38_incl",
    "vat_purchase_38_incl",
    "vat_purchase_38_invest_incl",
    "vat_sale_81_incl",
    "vat_purchase_81_incl",
    "vat_purchase_81_invest_incl",
    "l10n_cn_sales_included_13",
    "l10n_cn_sales_included_9",
    "l10n_cn_sales_included_6",
    "l10n_cn_tax_large_bis_sales_included_13",
    "l10n_cn_tax_large_bis_sales_included_9",
    "l10n_cn_tax_large_bis_sales_included_6",
    "l10n_cz_not_included_vat",
    "tax_ust_19_taxinclusive_skr03",
    "tax_ust_7_taxinclusive_skr03",
    "tax_vst_19_taxinclusive_skr03",
    "tax_vst_7_taxinclusive_skr03",
    "tax_ust_19_taxinclusive_skr04",
    "tax_ust_7_taxinclusive_skr04",
    "tax_vst_19_taxinclusive_skr04",
    "tax_vst_7_taxinclusive_skr04",
    "tax_18_sale_incl",
    "tax_18_purch_incl",
    "tax_16_purch_incl",
    "tax_9_purch_incl",
    "tax_8_purch_incl",
    "tax_18_purch_serv_incl",
    "tax_dom_purchase_brutto_25_5",
    "tax_dom_purchase_brutto_24",
    "tax_dom_purchase_brutto_14",
    "tax_dom_purchase_brutto_10",
    "l10n_jp_tax_sale_incl_8",
    "l10n_jp_tax_sale_incl_10",
    "l10n_jp_tax_purchase_incl_8",
    "l10n_jp_tax_purchase_incl_10",
    "l10n_kz_tax_vat_12_sale_included",
    "l10n_kz_tax_vat_12_purchase_included",
    "l10n_kz_tax_vat_20_sale_included",
    "l10n_kz_tax_vat_20_purchase_included",
    "l10n_kz_tax_vat_12_sale_included_export",
    "l10n_kz_tax_vat_12_purchase_included_import",
    "l10n_kz_tax_vat_20_sale_included_export",
    "l10n_kz_tax_vat_20_purchase_included_import",
    "l10n_kz_tax_vat_12_sale_included_eeu",
    "l10n_kz_tax_vat_12_purchase_included_eeu",
    "l10n_kz_tax_vat_20_sale_included_eeu",
    "l10n_kz_tax_vat_20_purchase_included_eeu",
    "btw_9_buy_incl",
    "btw_21_buy_incl",
    "nz_tax_sale_inc_15",
    "nz_tax_purchase_inc_15",
    "sale_tax_igv_18_included",
    "purchase_tax_igv_18_included",
    "tw_tax_sale_inc_5",
    "tw_tax_purchase_inc_5",
    "sale_tax_template_vat20incl_psbo",
    "sale_tax_template_vat14incl_psbo",
    "sale_tax_template_vat7incl_psbo",
    "purchase_tax_template_vat20incl_psbo",
    "purchase_tax_template_vat14incl_psbo",
    "purchase_tax_template_vat7incl_psbo",
)


def migrate(cr, version):
    util.create_column(cr, "res_company", "account_price_include", "varchar", default="tax_excluded")
    util.create_column(cr, "account_tax", "price_include_override", "varchar")
    cr.execute(
        """
            UPDATE account_tax t
               SET active = FALSE
              FROM ir_model_data md
             WHERE md.model = 'account.tax'
               AND md.res_id = t.id
               AND SUBSTRING(md.name, POSITION('_' in md.name) + 1) IN %s
               AND t.active
         RETURNING t.id, t.name->>'en_US'
        """,
        [DEACTIVATE_TAXES],
    )

    if cr.rowcount:
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        Taxes will now align by default with a company-wide setting for tax-included or excluded prices.
                        While most taxes will be adjusted automatically, some specific configurations may require review or manual adjustments.
                        We recommend verifying the following:
                        <ul>
                            <li>Your default company tax setting (included or excluded).</li>
                            <li>Any taxes with custom settings that may override the default.</li>
                            <li>Impacted reports or documents relying on tax values.</li>
                        </ul>
                        Please review the detailed list below of the taxes concerned (disabled by the upgrade) to ensure a smooth transition:
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(
                " ".join(
                    [
                        f"<li>{util.get_anchor_link_to_record('account.tax', id, name)}</li>"
                        for id, name in cr.fetchall()
                    ]
                )
            ),
            category="Account tax",
            format="html",
        )

    util.explode_execute(
        cr,
        """
            UPDATE account_tax t
               SET price_include_override = 'tax_included'
             WHERE price_include = TRUE
        """,
        table="account_tax",
        alias="t",
    )
    util.remove_column(cr, "account_tax", "price_include")

    util.remove_field(cr, "res.partner", "has_unreconciled_entries")
    util.remove_field(cr, "res.partner", "last_time_entries_checked")

    util.rename_field(cr, "res.config.settings", "module_account_sepa", "module_account_iso20022")

    cr.execute(
        """
        WITH line2account AS (
            SELECT line.id,
                   CASE
                       WHEN method.payment_type = 'inbound'
                       THEN company.account_journal_payment_debit_account_id
                       ELSE company.account_journal_payment_credit_account_id
                   END AS account
              FROM account_payment_method_line line
              JOIN account_journal journal
                ON line.journal_id = journal.id
              JOIN res_company company
                ON journal.company_id = company.id
              JOIN account_payment_method method
                ON line.payment_method_id = method.id
             WHERE line.payment_account_id IS NULL
        )
        UPDATE account_payment_method_line line
           SET payment_account_id = line2account.account
          FROM line2account
         WHERE line.id = line2account.id
        """
    )

    util.remove_field(cr, "res.config.settings", "account_journal_payment_debit_account_id")
    util.remove_field(cr, "res.config.settings", "account_journal_payment_credit_account_id")
    util.remove_field(cr, "res.company", "account_journal_payment_debit_account_id", drop_column=False)
    util.remove_field(cr, "res.company", "account_journal_payment_credit_account_id", drop_column=False)
    util.remove_field(cr, "account.payment", "destination_journal_id")
    util.remove_field(cr, "account.payment", "is_internal_transfer")

    util.rename_field(cr, "account.move", "payment_id", "origin_payment_id")
    util.rename_field(cr, "account.payment", "is_move_sent", "is_sent")
    util.create_column(cr, "account_payment", "is_sent", "boolean")
    util.rename_field(cr, "account.payment", "ref", "memo")
    util.create_column(cr, "account_payment", "memo", "varchar")
    util.rename_field(cr, "account.payment", "duplicate_move_ids", "duplicate_payment_ids")
    util.rename_field(cr, "account.payment.register", "duplicate_move_ids", "duplicate_payment_ids")
    util.create_column(cr, "account_payment", "name", "varchar")
    util.create_column(cr, "account_payment", "state", "varchar")
    util.create_column(cr, "account_payment", "date", "date")
    query_update_payment_from_move = """
        UPDATE account_payment
           SET name = move.name,
               memo = move.ref,
               date = move.date,
               is_sent = move.is_move_sent,
               state = CASE WHEN move.state = 'draft' THEN 'draft'
                            WHEN move.state = 'posted' AND NOT account_payment.is_matched THEN 'in_process'
                            WHEN move.state = 'posted' AND account_payment.is_matched THEN 'paid'
                            WHEN move.state = 'cancel' THEN 'canceled'
                            ELSE 'draft'
                       END
          FROM account_move move
         WHERE move.origin_payment_id = account_payment.id
    """
    util.explode_execute(cr, query_update_payment_from_move, table="account_payment")

    util.remove_inherit_from_model(
        cr,
        model="account.payment",
        inherit="account.move",
        keep=(
            "name",
            "state",
            "date",
            "currency_id",
            "company_id",
            "journal_id",
            "partner_id",
            "partner_bank_id",
            "payment_reference",
            "attachment_ids",
            "need_cancel_request",
            "expense_sheet_id",
            "need_cancel_request",
            "sdd_mandate_id",
            "sdd_mandate_scheme",
            "bacs_ddi_id",
            # mail.thread
            "activity_ids",
            "message_follower_ids",
            "message_ids",
            "message_main_attachment_id",
            "website_message_ids",
            "rating_ids",
            # localizations
            "l10n_in_withhold_move_ids",
            "l10n_in_total_withholding_amount",
            "l10n_ma_reports_payment_method",
        ),
    )
    util.remove_model(cr, "account.move.send")
    util.remove_field(cr, "res.company", "invoice_is_download")
    util.remove_field(cr, "res.company", "invoice_is_email")
    util.remove_field(cr, "res.config.settings", "invoice_is_download")
    util.remove_field(cr, "res.config.settings", "invoice_is_email")
    util.rename_field(cr, "account.move", "send_and_print_values", "sending_data")
    util.move_field_to_module(cr, "res.partner", "ubl_cii_format", "account_edi_ubl_cii", "account")
    util.rename_field(cr, "res.partner", "ubl_cii_format", "invoice_edi_format_store")
    util.make_field_company_dependent(cr, "res.partner", "invoice_edi_format_store", "selection")
    util.remove_record(cr, "account.account_move_send_single_rule_group_invoice")

    util.remove_view(cr, "account.tax_groups_totals")
    util.remove_field(cr, "account.tax", "total_tax_factor")
    util.remove_field(cr, "account.move.line", "tax_key")
    util.remove_field(cr, "account.move.line", "compute_all_tax")
    util.remove_field(cr, "account.move.line", "compute_all_tax_dirty")
