from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_it.tax_monthly_report_vat_balance")
    util.remove_records(
        cr,
        "account.report.line",
        [
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp6a"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp6b"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14a"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14b"),
        ],
    )
    util.remove_records(
        cr,
        "account.report.expression",
        [
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp6a_formula"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp6b_formula"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp7_balance"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp8_balance"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp9_balance"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14a_vp4_vp5_dif_pos"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14a_vp4_vp5_dif_neg"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14a_balance"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14a_carryover"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14b_vp4_vp5_dif_pos"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14b_vp4_vp5_dif_neg"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14b_balance"),
            util.ref(cr, "l10n_it.tax_monthly_report_line_vp14b_carryover"),
        ],
    )
