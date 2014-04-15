# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # mail_thread is an abstract model and does not have any table in DB
    if util.table_exists(cr, 'mail_thread'):
        cr.execute('DROP TABLE mail_thread')
