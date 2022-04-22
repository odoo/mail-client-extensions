# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides.slide_edit_options")
    util.remove_view(cr, "website_slides.user_navbar_inherit_website_slides")
