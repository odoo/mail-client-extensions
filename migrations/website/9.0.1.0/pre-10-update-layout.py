# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # XXX probably not enough, but it's a first step
    util.force_noupdate(cr, 'website.layout', False)
