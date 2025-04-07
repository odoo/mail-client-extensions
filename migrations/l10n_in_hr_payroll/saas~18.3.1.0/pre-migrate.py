from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_in_hr_payroll.hr_tds_register")
