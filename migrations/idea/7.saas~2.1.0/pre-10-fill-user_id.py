# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    util.create_column(cr, 'idea_idea', 'user_id', 'int4')
    cr.execute("UPDATE idea_idea SET user_id = create_uid WHERE user_id IS NULL")
