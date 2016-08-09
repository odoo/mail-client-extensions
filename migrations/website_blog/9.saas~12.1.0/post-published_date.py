# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE blog_post SET published_date = create_date WHERE website_published = true")
