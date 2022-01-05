# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # 1. the 'webpage' slide type is renamed to 'article'
    # 2. all slides of type 'presentation' are converted to 'document'
    util.change_field_selection_values(
        cr, "slide.slide", "slide_type", {"webpage": "article", "presentation": "document"}
    )

    # a few fields renaming
    util.rename_field(cr, "slide.slide", "slide_type", "slide_category")
    util.rename_field(cr, "slide.slide", "datas", "binary_content")
    util.rename_field(cr, "slide.slide", "nbr_webpage", "nbr_article")
    util.rename_field(cr, "slide.channel", "nbr_webpage", "nbr_article")

    # we actually re-introduce slide_type here, as a new concept (more granularity)
    util.create_column(cr, "slide_slide", "slide_type", "varchar")

    # "document_id" is renamed "google_drive_id" ans is now computed and non-stored
    util.remove_column(cr, "slide_slide", "document_id")
    util.rename_field(cr, "slide.slide", "document_id", "google_drive_id")

    # remove some fields that are now useless
    util.remove_field(cr, "slide.slide", "mime_type")
    util.remove_field(cr, "slide.slide", "nbr_presentation")
    util.remove_field(cr, "slide.channel", "nbr_presentation")

    # links are now resources
    util.remove_menus(cr, [util.ref(cr, "website_slides.website_slides_menu_courses_reviews")])
    util.remove_record(cr, "website_slides.rating_rating_action_slide_channel_report")
    util.create_column(cr, "slide_slide_resource", "resource_type", "varchar", default="file")
    util.create_column(cr, "slide_slide_resource", "link", "varchar")
    util.create_column(cr, "slide_slide_resource", "file_name", "varchar")

    util.create_column(cr, "slide_slide_resource", "_old_id", "int4")
    cr.execute(
        """
        INSERT INTO slide_slide_resource (_old_id, resource_type, name, slide_id, link)
             SELECT  id, 'url', name, slide_id, link
               FROM slide_slide_link
          RETURNING _old_id, id
        """
    )
    id_map = dict(cr.fetchall())
    if id_map:
        util.replace_record_references_batch(cr, id_map, model_src="slide.slide.link", model_dst="slide.slide.resource")
    util.remove_column(cr, "slide_slide_resource", "_old_id")

    util.remove_field(cr, "slide.slide", "link_ids")
    util.merge_model(cr, "slide.slide.link", "slide.slide.resource")

    util.rename_field(cr, "slide.slide", "embedcount_ids", "embed_ids")
