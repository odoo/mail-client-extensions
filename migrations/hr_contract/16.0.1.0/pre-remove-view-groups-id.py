from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_contract.hr_contract_manager_view_form")
