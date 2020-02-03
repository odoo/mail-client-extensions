# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "website_blog.menu_news", "website_blog.menu_blog")

    util.create_column(cr, "blog_blog", "content", "text")
    util.create_column(cr, "blog_blog", "cover_properties", "text")
    cr.execute(
        """
        UPDATE blog_blog
           SET cover_properties =
                '{"background-image": "none", "background-color": "oe_black", "opacity": "0.2", "resize_class": "cover_mid"}'
    """
    )

    util.remove_field(cr, "blog.post", "ranking")

    # update "resize_class" in blog_post.cover_properties json
    cr.execute(
        """
        UPDATE blog_post
           SET cover_properties = jsonb_pretty(jsonb_set(cover_properties::jsonb, '{resize_class}', '"cover_mid"'))
         WHERE cover_properties::json->>'resize_class' = ''
    """
    )
