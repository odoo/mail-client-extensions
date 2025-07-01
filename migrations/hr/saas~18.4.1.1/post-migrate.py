from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr.ir_rule_hr_contract_manager")
