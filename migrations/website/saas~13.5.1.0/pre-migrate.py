# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    for inh in util.for_each_inherit(cr, "website.seo.metadata", skip=()):
        table = util.table_of_model(cr, inh.model)
        if util.table_exists(cr, table):
            util.create_column(cr, table, "seo_name", "varchar")

    util.create_column(cr, "website_page", "header_visible", "boolean", default=True)
    util.create_column(cr, "website_page", "footer_visible", "boolean", default=True)
    util.create_column(cr, "website_page", "cache_time", "integer", default=0)
    util.create_column(cr, "website_page", "cache_key_expr", "varchar")

    # Reattach the base and COWed views for the cookie bar to the right
    # inherited view. The cookie bar template was
    # inheriting the footer_custom view before so we have to remove the COWed
    # ones before moving on the footer template migration. By simplicity, just
    # remove the view before it is re-created correctly when upgrading website.
    cr.execute("SELECT website_id, id FROM ir_ui_view WHERE key = 'website.layout'")
    layout_views = dict(cr.fetchall())
    cr.execute("SELECT id, website_id FROM ir_ui_view WHERE key = 'website.cookies_bar'")
    for (view_id, website_id) in cr.fetchall():
        inherit_id = layout_views.get(website_id, layout_views.get(None))
        cr.execute(
            "UPDATE ir_ui_view SET inherit_id = %s WHERE id = %s",
            [inherit_id, view_id],
        )

    # Snippets & templates
    util.remove_view(cr, "website.s_color_blocks_2_options")
    util.remove_view(cr, "website.s_masonry_block_options")
    util.remove_view(cr, "website.s_text_highlight_options")
    util.remove_view(cr, "website.option_custom_body_image")
    util.remove_view(cr, "website.option_custom_body_pattern")
    util.remove_view(cr, "website.option_layout_boxed_variables")

    util.rename_xmlid(cr, "website.snippet_options_border", "website.snippet_options_border_widgets")
    util.rename_xmlid(cr, "website.snippet_options_shadow", "website.snippet_options_shadow_widgets")
    util.rename_xmlid(cr, "website.website_name", "website.option_header_brand_name")
    util.rename_xmlid(cr, "website.layout_logo_show", "website.option_header_brand_logo")

    # All old header templates have been replaced by new ones. We have to remove
    # all the old ones and let the new default one being created, active. The
    # associated css variable have also been changed so we have to ensure the
    # users continue with the default header, which has no related css.
    util.remove_view(cr, "website.template_header_hamburger")
    util.remove_view(cr, "website.template_header_navbar_text_center")
    util.remove_view(cr, "website.template_header_hamburger_left")
    util.remove_view(cr, "website.header_shadow")

    # Note: this is done in website and not website_twitter_wall as the
    # COWed views need to be removed before moving on the footer template
    # migration.
    util.remove_view(cr, "website_twitter_wall.twitter_wall_footer_custom")

    # All old footer templates have been replaced by new ones. We have to remove
    # all the old ones and reenabling the "footer_custom" one which is still
    # there. For that, we delete the views which were COW'ed.
    cr.execute(
        """
           SELECT id
             FROM ir_ui_view
            WHERE key = 'website.footer_custom'
              AND website_id IS NOT NULL
              AND active = false
        """
    )
    for (vid,) in cr.fetchall():
        util.remove_view(cr, view_id=vid, key="website.footer_custom")

    util.remove_view(cr, "website.template_footer_logo_about_us_below")
    util.remove_view(cr, "website.template_footer_links_address_logo")
    util.remove_view(cr, "website.template_footer_name_logo_links_about_us")
    util.remove_view(cr, "website.template_footer_logo_only")
    util.remove_view(cr, "website.template_footer_address_logo")
