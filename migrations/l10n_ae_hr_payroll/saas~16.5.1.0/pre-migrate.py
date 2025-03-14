from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_end_of_service_salary_rule")
