# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'note_note', 'user_id', 'int4')
    cr.execute("UPDATE note_note SET user_id=create_uid")
