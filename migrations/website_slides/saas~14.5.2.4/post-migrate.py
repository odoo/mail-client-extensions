# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "website_slides.slide_template_published", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "website_slides.slide_template_shared", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "website_slides.mail_template_channel_completed", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "website_slides.mail_template_slide_channel_invite", util.update_record_from_xml, **rt)
