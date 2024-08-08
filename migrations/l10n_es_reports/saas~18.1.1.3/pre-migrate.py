from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(
        cr, "l10n_es_reports_modelo130.aeat.boe.mod130.export.wizard", "l10n_es_reports.aeat.boe.mod130.export.wizard"
    )
