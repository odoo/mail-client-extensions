# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mass.mailing.config.settings', 'group_website_popup_on_exit')
