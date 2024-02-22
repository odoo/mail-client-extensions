from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{3_lub_5,5}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{3_lub_5,5}_tag"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{7_lub_8,8}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{7_lub_8,8}_tag"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{22_lub_23,23}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_kraj_{22_lub_23,23}_tag"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{3_lub_5,5}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{3_lub_5,5}_tag"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{7_lub_8,8}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{7_lub_8,8}_tag"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{22_lub_23,23}"))
    util.rename_xmlid(cr, *eb("l10n_pl.account_tax_report_line_podatek_kraj_{22_lub_23,23}_tag"))
