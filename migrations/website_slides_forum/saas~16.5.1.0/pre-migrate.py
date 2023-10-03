# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_post_signed_in_user", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_tag_signed_in_user", util.update_record_from_xml)
