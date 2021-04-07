from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_helpdesk_forum.forum_posts_page")
