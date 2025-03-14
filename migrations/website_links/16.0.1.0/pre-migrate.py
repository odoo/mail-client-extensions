from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_links.share_page_menu")
