# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "slide.channel.partner", "completion", "completed_slides_count")
    util.create_column(cr, "slide_channel_partner", "completion", "integer")

    util.create_column(cr, "slide_channel", "description_short", "text")

    util.create_column(cr, "slide_answer", "sequence", "integer")
    cr.execute("UPDATE slide_answer SET sequence = id")

    util.rename_xmlid(cr, "website_slides.slides_share", "website_slides.slide_share_social")
    util.remove_view(cr, "website_slides.slide_social_media")
