# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'auth_signup.signup', False)
    util.force_noupdate(cr, 'auth_signup.reset_password', False)
