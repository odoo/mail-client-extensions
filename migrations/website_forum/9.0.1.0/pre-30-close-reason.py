# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'forum_post_reason', 'reason_type', 'varchar')
    cr.execute("UPDATE forum_post_reason SET reason_type='basic'")
