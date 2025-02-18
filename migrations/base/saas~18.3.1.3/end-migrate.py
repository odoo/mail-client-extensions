from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "base.default_user")
