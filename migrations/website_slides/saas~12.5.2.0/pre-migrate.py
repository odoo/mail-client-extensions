# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "module_website_slides_forum", "boolean")
    util.create_column(cr, "res_config_settings", "module_website_slides_survey", "boolean")
    util.create_column(cr, "res_config_settings", "module_mass_mailing_slides", "boolean")

    util.rename_field(cr, "slide.channel.tag.group", "website_published", "is_published")

    util.create_column(cr, "slide_channel", "color", "int4")
    cr.execute("UPDATE slide_channel SET color = 0 WHERE color IS NULL")
    util.remove_field(cr, "slide.channel", "category_ids")

    # remove leftover constraint that should have been dropped during saas~12.2 upgrade
    # (this has now be fixed by 3d30119f542fde796b4f8003a58f0976abb72a20)
    cr.execute("ALTER TABLE slide_slide DROP CONSTRAINT IF EXISTS slide_slide_name_uniq")

    # remove `rating.mixin` from `slide.slide`
    for suffix in {"ids", "last_value", "last_feedback", "last_image", "count", "avg"}:
        util.remove_field(cr, "slide.slide", "rating_" + suffix)
    cr.execute("DELETE FROM rating_rating WHERE res_model = 'slide.slide'")

    util.create_column(cr, "slide_slide", "is_category", "boolean")
    stat_fields = [
        field
        for field in [
            "nbr_presentation",
            "nbr_document",
            "nbr_video",
            "nbr_infographic",
            "nbr_webpage",
            "nbr_quiz",
            "total_slides",
            "nbr_certification",  # added by `website_slides_survey` module
        ]
        if util.column_exists(cr, "slide_category", field)
    ]

    for field in stat_fields:
        util.create_column(cr, "slide_slide", field, "int4")

    set_fields = ",".join("{} = 0".format(f) for f in stat_fields)
    cr.execute(
        """
            UPDATE slide_slide
               SET is_category = false,
                   {}
        """.format(
            set_fields
        )
    )

    util.remove_field(cr, "slide.slide", "index_content")
    util.remove_field(cr, "slide.slide", "category_sequence")
    cr.execute("ALTER TABLE slide_slide RENAME COLUMN category_id TO _old_category_id")
    util.create_column(cr, "slide_slide", "category_id", "int4")

    cr.execute(
        """
            INSERT INTO slide_slide(_old_category_id, name, sequence, channel_id, is_category, slide_type, {0}, active)
                 SELECT id, name, sequence, channel_id, true, 'document', {0}, TRUE
                   FROM slide_category
        """.format(
            ",".join(stat_fields)
        )
    )

    cr.execute(
        """
            UPDATE slide_slide s
               SET category_id = c.id
              FROM slide_slide c
             WHERE s.is_category = false
               AND c.is_category = true
               AND c._old_category_id = s._old_category_id
        """
    )

    # TODO verify that the sequence of categories are OK.
    util.remove_column(cr, "slide_slide", "_old_category_id")
    util.remove_model(cr, "slide.category")
