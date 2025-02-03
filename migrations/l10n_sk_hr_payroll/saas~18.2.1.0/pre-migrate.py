from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_sk_hr_payroll.work_entry_type_sick_25")
    util.force_noupdate(cr, "l10n_sk_hr_payroll.work_entry_type_sick_55")
    util.force_noupdate(cr, "l10n_sk_hr_payroll.work_entry_type_sick_0")
    util.force_noupdate(cr, "l10n_sk_hr_payroll.work_entry_type_maternity")
    util.force_noupdate(cr, "l10n_sk_hr_payroll.work_entry_type_parental_time_off")
