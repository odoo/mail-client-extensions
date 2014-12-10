# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'google_account.view_users_gogole_form')
    util.remove_view(cr, 'google_account.view_google_login_form')

