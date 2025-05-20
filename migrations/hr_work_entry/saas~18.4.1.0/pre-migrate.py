from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.work.entry", "contract_id", "version_id")

    util.remove_view(cr, "hr_work_entry.hr_work_entry_contract_view_form_inherit")
    util.remove_view(cr, "hr_work_entry.hr_work_entry_contract_view_calendar_inherit")
    util.remove_view(cr, "hr_work_entry.hr_work_entry_contract_type_view_form_inherit")
    util.remove_view(cr, "hr_work_entry.hr_contract_view_form_inherit_work_entry")
