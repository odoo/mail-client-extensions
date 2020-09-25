# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "blog_post", "website_id", "int4")
    cr.execute("UPDATE blog_post p SET website_id = b.website_id FROM blog_blog b WHERE b.id = p.blog_id")
