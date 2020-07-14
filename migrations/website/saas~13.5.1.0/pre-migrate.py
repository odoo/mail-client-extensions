# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "website_page", "header_visible", "boolean", default=True)
    util.create_column(cr, "website_page", "footer_visible", "boolean", default=True)

    util.remove_view(cr, "website.s_color_blocks_2_options")
    util.remove_view(cr, "website.s_masonry_block_options")
    util.remove_view(cr, "website.s_text_highlight_options")
    util.rename_xmlid(cr, "website.snippet_options_border", "website.snippet_options_border_widgets")
    util.rename_xmlid(cr, "website.snippet_options_shadow", "website.snippet_options_shadow_widgets")
