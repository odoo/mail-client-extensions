# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'base_setup.view_general_configuration')
    util.remove_view(cr, 'base_setup.assets_backend')
