from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "res.partner", "sanitized_phone", "phone")
    util.remove_field(cr, "res.partner", "sanitized_phone")
    util.update_field_usage(cr, "res.partner", "sanitized_mobile", "mobile")
    util.remove_field(cr, "res.partner", "sanitized_mobile")
