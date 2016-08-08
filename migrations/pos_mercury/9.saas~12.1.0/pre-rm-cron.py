# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'pos_mercury.ir_cron_mercury_cleanup')
