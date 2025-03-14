from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.au.tax.report")
    util.remove_view(cr, "l10n_au_reports.line_caret_options")
