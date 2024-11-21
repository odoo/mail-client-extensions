from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_hr_expense.ir_actions_server_create_hr_expense")
