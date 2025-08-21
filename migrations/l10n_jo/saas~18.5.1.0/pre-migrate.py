from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_purchase_import_{,base_}sixteen_tag"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_purchase_import_{,base_}ten_tag"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_purchase_import_{,base_}four_tag"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_purchase_import_{,base_}other_tag"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_sales_{export_zero,exported}"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_sale_{export_zero_,exported_base_}tag"))
    util.rename_xmlid(cr, *eb("l10n_jo.tax_report_vat_sale_export_no_deductible_zero_{tag_tax,tax_tag}"))

    report_line_records = [
        util.ref(cr, "l10n_jo.tax_report_vat_purchase_base"),
        util.ref(cr, "l10n_jo.tax_report_vat_sales_zero"),
        util.ref(cr, "l10n_jo.tax_report_vat_return_net"),
        util.ref(cr, "l10n_jo.tax_report_vat_payable"),
        util.ref(cr, "l10n_jo.tax_report_vat_recoverable"),
        util.ref(cr, "l10n_jo.tax_report_vat_net_due"),
    ]

    report_expression_records = [
        util.ref(cr, "l10n_jo.tax_report_vat_purchase_base_aggregation"),
        util.ref(cr, "l10n_jo.tax_report_vat_purchase_tax_aggregation"),
        util.ref(cr, "l10n_jo.tax_report_vat_purchase_exempt_tax_tag"),
        util.ref(cr, "l10n_jo.tax_report_vat_purchase_deferred_supply_tax_tag"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_export_zero_tag_tax"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_export_exempt_local_zero_tag_tax"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_export_no_tax_zero_tag_tax"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_export_no_deductible_zero_tag"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_zero_tag"),
        util.ref(cr, "l10n_jo.tax_report_vat_sale_zero_tag_tax"),
    ]

    util.remove_records(cr, "account.report.line", report_line_records)
    util.remove_records(cr, "account.report.expression", report_expression_records)

    # It updates the suffixes of tax tags as per the new naming convention for tax tags.
    # '(Base)' is changed to '_b' and '(Tax)' is changed to '_t'.
    jordan_country_id_filter = cr.mogrify("t.country_id = %s", (util.ref(cr, "base.jo"),)).decode()
    util.replace_in_all_jsonb_values(
        cr,
        "account_account_tag",
        "name",
        util.PGRegexp(r" \(Base\)"),
        util.PGRegexp(r"_b"),
        extra_filter=jordan_country_id_filter,
    )
    util.replace_in_all_jsonb_values(
        cr,
        "account_account_tag",
        "name",
        util.PGRegexp(r" \(Tax\)"),
        util.PGRegexp(r"_t"),
        extra_filter=jordan_country_id_filter,
    )
    util.replace_in_all_jsonb_values(
        cr,
        "account_account_tag",
        "name",
        util.PGRegexp(r"^7"),
        util.PGRegexp(r"7b"),
        extra_filter=jordan_country_id_filter,
    )

    # Some report lines are moved out of their parent and put at the root of the report.
    # This ensures it is displayed at the correct heirarchy level in the report UI.
    report_line_xmlids = (
        "tax_report_vat_sales_exported",
        "tax_report_vat_sales_no_tax_zero",
        "tax_report_vat_sales_exempt_local_zero",
        "tax_report_vat_sales_no_deductible_zero",
        "tax_report_vat_purchase_deferred_supply",
        "tax_report_vat_purchase_exempt",
    )
    cr.execute(
        """
        UPDATE account_report_line line
           SET parent_id = NULL, hierarchy_level = 1
          FROM ir_model_data imd
         WHERE imd.res_id = line.id
           AND imd.model = 'account.report.line'
           AND imd.module = 'l10n_jo'
           AND imd.name IN %s
           AND (line.parent_id IS NOT NULL OR line.hierarchy_level != 1)
        """,
        [report_line_xmlids],
    )
