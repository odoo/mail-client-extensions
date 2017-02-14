# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'account.online.journal', 'institution_id')
    util.delete_model(cr, 'account.institution')
