from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_ke.master.report")
    util.remove_view(cr, "l10n_ke_hr_payroll.report_master_report")
