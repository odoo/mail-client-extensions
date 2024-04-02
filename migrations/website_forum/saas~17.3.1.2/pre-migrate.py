from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "forum.forum", "menu_id")
