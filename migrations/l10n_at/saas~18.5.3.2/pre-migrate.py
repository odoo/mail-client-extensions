from odoo.upgrade import util


def migrate(cr, version):

    # Remove obsolete report lines to avoid duplicates/conflicts when updating XML
    older_records = [
        "l10n_at.tax_report_line_l10n_at_tva_line_4_14_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_15_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_16_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_17_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_18_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_19_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_14_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_15_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_16_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_17_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_18_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_19_tax",
        "l10n_at.tax_report_line_at_base_title_umsatz_base_4_14_19",
        "l10n_at.tax_report_line_at_tax_title_4_14_19",
        "l10n_at.tax_report_line_at_base_title_umsatz_base_4_28_31",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_28_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_29_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_30_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_31_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_28_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_29_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_30_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_31_tax",
        "l10n_at.tax_report_line_at_tax_title_4_28_31",
        "l10n_at.tax_report_line_l10n_at_tva_line_5_13_tag",
    ]
    for xid in older_records:
        util.remove_record(cr, xid)
