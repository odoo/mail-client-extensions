from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users.settings", "is_discuss_sidebar_category_livechat_open")
