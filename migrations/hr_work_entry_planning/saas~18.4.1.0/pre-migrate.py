from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_work_entry_planning.hr_contract_view_form_inherit_work_entry_planning")
