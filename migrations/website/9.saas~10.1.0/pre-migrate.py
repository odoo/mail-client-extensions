# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("DROP TABLE website_seo_metadata")   # should always have been a abstract model

    util.remove_view(cr, 'website.layout_editor')
