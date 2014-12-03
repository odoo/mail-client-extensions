# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # Move instances in picking_exception to cancel
    cr.execute("""
        UPDATE wkf_workitem
            SET act_id = (SELECT res_id FROM ir_model_data WHERE module='mrp' and name='prod_act_cancel' LIMIT 1)
            WHERE act_id = (SELECT res_id FROM ir_model_data WHERE module='mrp' and name='prod_act_picking_exception' LIMIT 1);
    """)

    # Move instances in picking to confirmed
    cr.execute("""
        UPDATE wkf_workitem
            SET act_id = (SELECT res_id FROM ir_model_data WHERE module='mrp' and name='prod_act_confirmed' LIMIT 1)
            WHERE act_id = (SELECT res_id FROM ir_model_data WHERE module='mrp' and name='prod_act_picking' LIMIT 1);
    """)