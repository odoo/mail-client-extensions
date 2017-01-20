# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'ga_sync ga_client_id ga_client_secret google_management_authorization'.split():
        util.remove_field(cr, 'base.config.settings', f)
