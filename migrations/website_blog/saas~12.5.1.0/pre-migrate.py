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
        # bb0cdec renamed .cover to .o_wblog_has_cover
        # 08cc073 replaced .o_wblog_has_cover by the more general .o_record_has_cover
        # empty resize_class are initialized with 'o_record_has_cover cover_mid' if there is a background image
        r"""
        UPDATE blog_post
            SET cover_properties = jsonb_set(cover_properties::jsonb, '{resize_class}',
                to_jsonb(REGEXP_REPLACE(
                    coalesce(cover_properties::jsonb->>'resize_class',
                        case when cover_properties::jsonb->>'background-image' <> 'none' then 'o_record_has_cover cover_mid'
                        else '' end
                    ),
                    '\m(cover(?!-)|o_wblog_has_cover)\M', 'o_record_has_cover', 'g'
                ))
            )
    """)
    cr.execute(
        # bb0cdec renamed the cover size 'container-fluid cover_full' -> 'cover_full'
        # => Remove container-fluid when resize_class contains 'container-fluid' and 'cover_full'
        r"""
        UPDATE blog_post
            SET cover_properties = jsonb_set(cover_properties::jsonb, '{resize_class}',
                to_jsonb(REGEXP_REPLACE(
                    cover_properties::jsonb->>'resize_class',
                    '\mcontainer-fluid\M', '', 'g')
                )
            )
            WHERE cover_properties::jsonb->>'resize_class' ~ '\mcontainer-fluid\M'
                AND cover_properties::jsonb->>'resize_class' ~ '\mcover_full\M'

    """)
    cr.execute(
        # bb0cdec renamed the cover size 'container-fluid cover_narrow' -> 'cover_mid'
        # => Remove container-fluid and rename 'cover_narrow' to 'cover_mid'
        # when resize_class contains 'container-fluid' and 'cover_narrow'
        r"""
        UPDATE blog_post
            SET cover_properties = jsonb_set(cover_properties::jsonb, '{resize_class}',
                to_jsonb(REGEXP_REPLACE(REGEXP_REPLACE(
                    cover_properties::jsonb->>'resize_class',
                    '\mcontainer-fluid\M', '', 'g'),
                    '\mcover_narrow\M', 'cover_mid', 'g')
                )
            )
            WHERE cover_properties::jsonb->>'resize_class' ~ '\mcontainer-fluid\M'
                AND cover_properties::jsonb->>'resize_class' ~ '\mcover_narrow\M'
    """)
    cr.execute(
        # bb0cdec renamed the cover size 'container cover_narrow' -> 'cover_auto'
        # => Remove container and rename 'cover_narrow' to 'cover_auto'
        # when resize_class contains 'container' and 'cover_narrow'
        r"""
        UPDATE blog_post
            SET cover_properties = jsonb_set(cover_properties::jsonb, '{resize_class}',
                to_jsonb(REGEXP_REPLACE(REGEXP_REPLACE(
                    cover_properties::jsonb->>'resize_class',
                    '\mcontainer(?!-)\M', '', 'g'),
                    '\mcover_narrow\M', 'cover_auto', 'g')
                )
            )
            WHERE cover_properties::jsonb->>'resize_class' ~ '\mcontainer(?!-)\M'
                AND cover_properties::jsonb->>'resize_class' ~ '\mcover_narrow\M'
    """)
