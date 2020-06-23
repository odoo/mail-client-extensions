# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_slides_forum.access_forum_forum_website_publisher")
