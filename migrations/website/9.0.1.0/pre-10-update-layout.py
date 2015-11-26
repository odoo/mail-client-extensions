# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'website.layout', False)
    util.force_noupdate(cr, 'website.500', False)
    util.force_noupdate(cr, 'website.template_partner_comment', False)      # demo data
