from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("l10n_dk_{rsu,reports}.tax.report.calendar.wizard"))
    util.rename_model(cr, *eb("l10n_dk_{rsu,reports}.tax.report.submit.draft.wizard"))
    util.rename_model(cr, *eb("l10n_dk_{rsu,reports}.tax.report.receipt.wizard"))
