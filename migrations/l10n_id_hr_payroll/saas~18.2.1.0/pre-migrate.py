from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_in_hr_payroll.work_entry_type_bereavement_leave")
    util.force_noupdate(cr, "l10n_in_hr_payroll.work_entry_type_marriage_leave")
    util.force_noupdate(cr, "l10n_in_hr_payroll.work_entry_type_maternity_leave")
    util.force_noupdate(cr, "l10n_in_hr_payroll.work_entry_type_paternity_leave")
    util.force_noupdate(cr, "l10n_in_hr_payroll.work_entry_type_public_holiday")
