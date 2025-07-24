from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "quality.check", "is_expired")
