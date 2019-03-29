# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, 'mrp.repair', 'repair.order')
    util.rename_model(cr, 'mrp.repair.line', 'repair.line')
    util.rename_model(cr, 'mrp.repair.fee', 'repair.fee')
    util.rename_model(cr, 'mrp.repair.cancel', 'repair.cancel')
    util.rename_model(cr, 'mrp.repair.make_invoice', 'repair.order.make_invoice')

    util.remove_field(cr, 'repair.order', 'location_dest_id')

    # computed later
    util.create_column(cr, 'repair_line', 'price_subtotal', 'numeric')
    util.create_column(cr, 'repair_fee', 'price_subtotal', 'numeric')

    renames = util.splitlines("""
        seq_{mrp_,}repair
        mail_template_{mrp_,}repair_quotation

        action_report_{mrp_,}repair_order
        report_{mrp,}repairorder
        report_{mrp,}repairorder2

        access_{mrp_,}repair_fee_user
        access_{mrp_,}repair_fee_manager
        access_{mrp_,}repair_user
        access_{mrp_,}repair_manager
        access_{mrp_,}repair_line_user
        access_{mrp_,}repair_line_manager
        access_{mrp_,}repair_fee_user_mrp
        access_{mrp_,}repair_fee_mgr

        {mrp_,}repair_rule

        view_{mrp_,}repair_kanban

        act_{mrp_,}repair_invoice

        # some demo data
        {mrp_repair_rmrp,repair_r}0
        {mrp_repair_rmrp,repair_r}1
        {mrp_repair_rmrp,repair_r}2
    """)
    for r in renames:
        util.rename_xmlid(cr, *eb('repair.' + r))

    cr.execute("""
        UPDATE ir_sequence
           SET code = 'repair.order'
         WHERE code = 'mrp.repair'
           AND id = %s
    """, [util.ref(cr, "repair.seq_repair")])
