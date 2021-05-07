# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "slide.channel", "description")
    util.convert_field_to_html(cr, "slide.channel", "description_short")
    util.convert_field_to_html(cr, "slide.slide", "description")
