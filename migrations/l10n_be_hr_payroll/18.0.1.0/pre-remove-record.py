from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_be_hr_payroll.holiday_status_bank_holiday", keep_xmlids=False)
