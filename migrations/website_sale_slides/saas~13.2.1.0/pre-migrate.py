# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_slides.course_sidebar")
    util.remove_view(cr, "website_sale_slides.course_sidebar_buy_now_course")
