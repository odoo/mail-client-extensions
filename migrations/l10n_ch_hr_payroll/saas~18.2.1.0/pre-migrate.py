from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_ch_hr_payroll.work_entry_type_bank_holiday")
