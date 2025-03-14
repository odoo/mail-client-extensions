from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.update_field_usage(cr, "hr.contract", "visa_expire", "employee_id.work_permit_expiration_date")
    util.remove_field(cr, "hr.contract", "visa_expire")
    util.rename_xmlid(cr, *eb("{hr_work_entry_contract_enterprise,hr_contract}.hr_menu_contract"), on_collision="merge")
