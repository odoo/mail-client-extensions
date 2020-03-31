# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_blog._assets_primary_variables")
    util.remove_view(cr, "website_blog.s_latest_posts_big_picture")
