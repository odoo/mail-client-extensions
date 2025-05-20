from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "l10n_au.payroll.finalisation.wizard.emp", "contract_id", "version_id")
