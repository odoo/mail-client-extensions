from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "report.l10n_ae_hr_payroll.master")
