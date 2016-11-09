# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # XXX is it correct? should we keep current journal?
    journal_id = util.ref(cr, 'point_of_sale.pos_sale_journal')
    cr.execute("UPDATE pos_config SET journal_id=%s", [journal_id])
