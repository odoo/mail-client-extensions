# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    """Remove sensitive data that are not used anymore"""
    util.remove_field(cr, 'res.user', 'gmail_user')
    util.remove_field(cr, 'res.user', 'gmail_password')
