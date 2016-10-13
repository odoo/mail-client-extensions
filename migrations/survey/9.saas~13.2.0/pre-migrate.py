# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # cron now part of ir.autovacuum
    util.remove_record(cr, 'survey.ir_cron_clean_empty_surveys')
