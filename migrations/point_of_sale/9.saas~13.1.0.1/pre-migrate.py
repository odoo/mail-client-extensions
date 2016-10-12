# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'pos.order')
    util.drop_workflow(cr, 'pos.session')

    util.create_column(cr, 'pos_config', 'invoice_journal_id', 'int4')
    cr.execute("UPDATE pos_config SET invoice_journal_id=journal_id")

    # action change type from client action to act_window -> force recreation
    util.remove_record(cr, 'point_of_sale.action_report_pos_details')
