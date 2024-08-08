from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "l10n_es_modelo130.mod130.tax.report.handler", "l10n_es.mod130.tax.report.handler")
