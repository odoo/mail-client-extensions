# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_model(cr, 'mail.test')
    for suffix in 'simple track activity full'.split():
        util.remove_model(cr, 'mail.test.' + suffix)
