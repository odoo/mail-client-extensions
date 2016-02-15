# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # FIXME background url will not work in 9.0
    # /website/image is not a valid route anymore
    cr.execute("""
        UPDATE blog_post
           SET cover_properties = concat('{"resize_class": "cover cover_full", "background-color": "oe_none", "background-image": "url(', encode(background_image, 'escape'), ')"}')
         WHERE background_image IS NOT NULL
    """)

    util.remove_field(cr, 'blog.post', 'background_image')
