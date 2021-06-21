# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_slides.mail_template_slide_channel_enroll", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.mail_notification_channel_invite", util.update_record_from_xml)
