from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_forum.user_profile_sub_nav")
