# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides.slide_icon")
    util.remove_view(cr, "website_slides.private_profile")
