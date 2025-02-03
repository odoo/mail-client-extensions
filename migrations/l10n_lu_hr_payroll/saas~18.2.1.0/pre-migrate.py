from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_lu_hr_payroll.work_entry_type_situational_unemployment")
