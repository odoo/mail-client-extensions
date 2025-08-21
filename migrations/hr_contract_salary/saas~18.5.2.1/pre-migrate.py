from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "hr.contract.salary.benefit.type", "name")
    util.convert_field_to_translatable(cr, "hr.contract.salary.personal.info.type", "name")
    util.convert_field_to_translatable(cr, "hr.contract.salary.resume.category", "name")
    util.convert_field_to_translatable(cr, "hr.contract.salary.resume", "name")
    util.remove_field(cr, "hr.contract.salary.personal.info", "position")
