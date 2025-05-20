from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_be_hr_payroll_fleet.hr_payroll_dashboard_warning_car_mismatch")
