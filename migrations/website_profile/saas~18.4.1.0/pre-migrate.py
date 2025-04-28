from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_profile.user_profile_edit_content")
    util.remove_view(cr, "website_profile.user_profile_edit_main")
    util.remove_view(cr, "website_profile.user_biography_editor")
