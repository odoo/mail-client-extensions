# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cid = util.ref(cr, 'calendar.ir_cron_scheduler_alarm')
    if cid:
        cr.execute("UPDATE ir_cron SET model=%s WHERE id=%s", ('calendar.alarm_manager', cid))
