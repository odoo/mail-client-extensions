# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "slide.channel", "website_background_image_url", "website_default_background_image_url")
