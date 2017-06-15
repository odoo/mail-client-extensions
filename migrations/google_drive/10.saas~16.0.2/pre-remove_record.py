# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.remove_record(cr, 'google_drive.menu_google_drive_model_config')
    util.remove_record(cr, 'google_drive.menu_google_drive_config')
