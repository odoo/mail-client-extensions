from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "test_themes.user_navbar")
