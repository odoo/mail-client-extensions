from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "res.partner", "website_description")
    util.convert_field_to_translatable(cr, "res.partner", "website_short_description")
