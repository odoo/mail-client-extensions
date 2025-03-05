from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_work_entry_contract.hr_work_entry_contract_type_view_form_inherit")
