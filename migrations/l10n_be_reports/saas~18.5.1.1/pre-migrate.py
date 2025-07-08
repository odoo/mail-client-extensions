from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "need_ec_sales_list")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "ask_restitution")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "is_prorata_necessary")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "show_prorata")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "prorata")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "prorata_year")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "prorata_at_100")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "prorata_at_0")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_deduction")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_1")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_2")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_3")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_4")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "special_prorata_5")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "submit_more")
