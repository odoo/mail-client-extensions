# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_column(cr, 'base_config_settings', 'google_drive_uri')
