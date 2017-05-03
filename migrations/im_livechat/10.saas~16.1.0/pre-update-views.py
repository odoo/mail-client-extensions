# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'im_livechat.external_lib', False)
