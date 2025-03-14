from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_ma_hr_payroll.hr_contract_type_emp")
    util.update_record_from_xml(cr, "l10n_ma_hr_payroll.hr_contract_type_wrkr")
    util.update_record_from_xml(cr, "l10n_ma_hr_payroll.hr_contract_type_sub")
