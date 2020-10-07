# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_monglia.header_image_1_default_image")
