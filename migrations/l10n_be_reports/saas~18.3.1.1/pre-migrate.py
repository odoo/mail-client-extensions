from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account_reports.export.wizard", "l10n_be_reports_periodic_vat_wizard_id")
    util.remove_model(cr, "l10n_be_reports.periodic.vat.xml.export")
