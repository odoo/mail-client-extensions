# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "slide_channel_tag", "color", "int4", default=0)
    util.fixup_m2m(cr, "rel_slide_tag", "slide_slide", "slide_tag", "slide_id", "tag_id")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_slides.website_slides_menu_config_course_{tags,groups}"))
