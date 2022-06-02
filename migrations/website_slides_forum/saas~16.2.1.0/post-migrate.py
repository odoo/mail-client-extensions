# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_public", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_public_post", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides_forum.website_slides_forum_public_tag", util.update_record_from_xml)
