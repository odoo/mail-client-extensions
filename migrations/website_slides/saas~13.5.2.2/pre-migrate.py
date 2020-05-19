# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides.display_promoted_slide")
    util.create_column(cr, "slide_channel", "promoted_slide_id", "int4")
    util.remove_field(cr, "slide.channel.invite", "channel_url")
