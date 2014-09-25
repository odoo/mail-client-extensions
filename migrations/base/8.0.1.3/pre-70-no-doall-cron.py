# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute('UPDATE ir_cron SET doall=false')
