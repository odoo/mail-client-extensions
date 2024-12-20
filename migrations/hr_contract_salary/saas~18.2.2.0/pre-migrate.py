from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_contract_salary.hr_contract_view_tree_contract_templates")
    util.remove_view(cr, "hr_contract_salary.hr_contract_view_form_contract_templates")
