from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.template", "country_code")
