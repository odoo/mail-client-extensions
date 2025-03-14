from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "l10n_pl_reports_jpk.periodic.vat.xml.export", "l10n_pl_reports.periodic.vat.xml.export")
