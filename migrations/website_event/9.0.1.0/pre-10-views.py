# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = "index event_category layout template_location event_details".split()
    for v in views:
        util.force_noupdate(cr, 'website_event.' + v, False)
