from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    lines_to_remove = [
        "l10n_ae.tax_report_line_expense_out_of_scope",
        "l10n_ae.tax_report_line_expense_out_of_scope_vat",
        "l10n_ae.tax_report_line_standard_rated_supplies_base_subtotal",
        "l10n_ae.tax_report_line_supplies_out_of_scope_base",
        "l10n_ae.tax_report_line_supplies_out_of_scope_vat",
        "l10n_ae.tax_report_line_vat_all_sales",
        "l10n_ae.tax_report_line_vat_all_expense",
    ]

    util.remove_records(
        cr,
        "account.report.line",
        [id for xmlid in lines_to_remove if (id := util.ref(cr, xmlid))],
    )

    util.remove_record(cr, "l10n_ae.tax_report_balance")

    def gen_mapping(xmlid, emirate=""):
        return (
            eb(f"{xmlid}{{_base,}}{emirate}"),
            eb(f"{xmlid}{{_base{emirate}_tag,{emirate}_base}}"),
            eb(f"{xmlid}{{_vat{emirate}_tag,{emirate}_tax}}"),
        )

    mappings = [
        eb("l10n_ae.tax_report_line_{base_,}all_sales"),
        eb("l10n_ae.tax_report_line_{base_,}all_sales_total"),
        eb("l10n_ae.tax_report_line_{base_,}all_expense"),
        eb("l10n_ae.tax_report_line_{base_,}all_expense_total"),
        eb("l10n_ae.tax_report_line_adjustment_import_uae{_base,}"),
        eb("l10n_ae.tax_report_line_adjustment_import_uae_base{_formula,}"),
        eb("l10n_ae.tax_report_line_adjustment_import_uae{_vat_formula,_tax}"),
        eb("l10n_ae.tax_report_line_exempt_supplies{_base,}"),
        eb("l10n_ae.tax_report_line_exempt_supplies_base{_tag,}"),
        eb("l10n_ae.tax_report_line_standard_rated_supplies{_base,}"),
        eb("l10n_ae.tax_report_line_zero_rated_supplies{_base,}"),
        eb("l10n_ae.tax_report_line_zero_rated_supplies_base{_tag,}"),
        *gen_mapping("l10n_ae.tax_report_line_expense_supplies_reverse"),
        *gen_mapping("l10n_ae.tax_report_line_import_uae"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_expense"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_abu_dhabi"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_dubai"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_sharjah"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_ajman"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_umm_al_quwain"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_ras_al_khaima"),
        *gen_mapping("l10n_ae.tax_report_line_standard_rated_supplies", emirate="_fujairah"),
        *gen_mapping("l10n_ae.tax_report_line_supplies_reverse_charge"),
        *gen_mapping("l10n_ae.tax_report_line_tax_refund_tourist"),
    ]

    for old, new in mappings:
        util.rename_xmlid(cr, old, new)

    util.update_record_from_xml(cr, "base.ae", fields=["vat_label", "state_required"])
    util.update_record_from_xml(cr, "base.AED", fields=["symbol"])

    # Aggregate formulas can only be used for 1 column, so we remove them since more records will be added
    # in the xml file which will use the aggregation engine.
    no_agg_formula_xmlids = [
        "l10n_ae.tax_report_line_all_expense",
        "l10n_ae.tax_report_line_all_expense_total",
        "l10n_ae.tax_report_line_all_sales",
        "l10n_ae.tax_report_line_all_sales_total",
        "l10n_ae.tax_report_line_net_vat_due",
        "l10n_ae.tax_report_line_net_vat_due_period",
        "l10n_ae.tax_report_line_standard_rated_supplies",
        "l10n_ae.tax_report_line_total_value_due_tax_period",
        "l10n_ae.tax_report_line_total_value_recoverable_tax_period",
    ]

    cr.execute(
        """
        DELETE FROM account_report_expression
              WHERE report_line_id = ANY(%s)
        """,
        [[id for xmlid in no_agg_formula_xmlids if (id := util.ref(cr, xmlid))]],
    )

    line_id = util.ref(cr, "l10n_ae.tax_report_line_adjustment_import_uae_tax")
    if line_id:
        cr.execute(
            """
            UPDATE account_report_expression
               SET subformula = NULL
             WHERE report_line_id = %s
               AND subformula IS NOT NULL
            """,
            [line_id],
        )

    # Archive the Sales RCM taxes as they are all redundant (reverse charge implies the inception is on a vendor bill ~ purchase tax)
    cr.execute(
        r"""
            UPDATE account_tax t
               SET active = FALSE
              FROM ir_model_data md
             WHERE md.model = 'account.tax'
               AND md.res_id = t.id
               AND md.name ~ '^\d+_uae_sale_tax_reverse_charge_(?:dubai|adu_dhabi|sharjah|ajman|umm_al_quwain|ras_al_khaima|fujairah)$'
               AND md.module = 'account'
               AND t.active IS NOT FALSE
        """
    )
