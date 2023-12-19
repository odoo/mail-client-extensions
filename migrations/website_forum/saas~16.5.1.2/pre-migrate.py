from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_forum.private_profile")

    # explictly reload noupdate views
    util.update_record_from_xml(cr, "website_forum.forum_post_view_form")
    util.update_record_from_xml(cr, "website_forum.forum_post_view_tree")
