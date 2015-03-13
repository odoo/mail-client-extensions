# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'website_event.event_description_full', False)
    util.force_noupdate(cr, 'website_event.layout', False)
