# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides.slide_icon")
    util.remove_view(cr, "website_slides.private_profile")

    util.if_unchanged(cr, "website_slides.rule_slide_channel_visibility_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.rule_slide_slide_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.rule_slide_slide_resource_downloadable", util.update_record_from_xml)
    util.remove_field(cr, "slide.channel", "partner_all_ids")

    util.remove_field(cr, "res.partner", "slide_channel_all_ids", drop_column=False)
