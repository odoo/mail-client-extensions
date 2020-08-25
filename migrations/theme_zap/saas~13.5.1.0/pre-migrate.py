# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_zap.image_content_07")
    util.remove_record(cr, "theme_zap.image_content_08")
    util.remove_record(cr, "theme_zap.image_content_09")
