from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "homework.location.wizard", "user_can_edit")
