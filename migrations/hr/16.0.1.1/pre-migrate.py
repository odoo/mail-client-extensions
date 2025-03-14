from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.move_model(cr, "hr.contract.type", "hr_contract", "hr")
    util.rename_xmlid(cr, *eb("hr{_contract,}.access_hr_contract_type_manager"))
