from odoo.upgrade.util import remove_view


def migrate(cr, version):
    remove_view(cr, "website.snippet_options_carousel_intro")
    remove_view(cr, "website.s_carousel_intro_options")
    remove_view(cr, "website.s_tabs_options")
    remove_view(cr, "website.view_server_action_tree_website")
