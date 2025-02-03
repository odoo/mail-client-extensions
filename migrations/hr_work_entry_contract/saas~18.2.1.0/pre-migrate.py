from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_leave")
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_compensatory")
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_home_working")
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_unpaid_leave")
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_sick_leave")
    util.force_noupdate(cr, "hr_work_entry_contract.work_entry_type_legal_leave")
