# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_blog.blog_post_template_new_post", noupdate=True)
