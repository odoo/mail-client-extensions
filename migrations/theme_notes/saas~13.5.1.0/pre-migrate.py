# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_notes.assets_frontend")
    util.remove_record(cr, "theme_notes.image_content_09")
    util.remove_record(cr, "theme_notes.image_content_10")
    util.remove_record(cr, "theme_notes.image_content_11")
    util.remove_record(cr, "theme_notes.image_content_12")
