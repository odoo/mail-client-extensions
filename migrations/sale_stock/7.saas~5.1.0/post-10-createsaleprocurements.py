from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.osv import fields, osv



def migrate(cr, version):
    """
        For all sale orders that are not delivered yet, create procurements 
        to these lines
    """
    
    # Check all related moves to sale order lines where the sales order is not done and not shipped and not cancelled
    # Create a procurement group for every sales order related, create a procurement in customers and
    # create a procurement in
    #
    registry = RegistryManager.get(cr.dbname)
    move_obj = registry["stock.move"]
    sol_obj = registry['sale.order.line']
    so_obj = registry['sale.order']
    proc_obj = registry['procurement.order']
    cr.execute("""SELECT sm.sale_line_id, sm.id FROM stock_move sm, sale_order_line sol, sale_order so, product_product pp, product_template pt WHERE so.shipped = False
    and so.state not in ('done', 'cancel') and pp.product_tmpl_id = pt.id
    and pt.type <> 'service' and pp.id = sol.product_id and so.id = sol.order_id and sm.sale_line_id = sol.id 
    """)
    sol_dict = {}
    for item in cr.fetchall():
        if not sol_dict.get(item[0]):
            sol_dict[item[0]] = [item[1]]
        else:
            sol_dict[item[0]] += [item[1]]
    for line in sol_obj.browse(cr, SUPERUSER_ID, sol_dict.keys()):
        order = line.order_id
        if not order.procurement_group_id:
            vals = so_obj._prepare_procurement_group(cr, SUPERUSER_ID, order)
            group_id = registry["procurement.group"].create(cr, SUPERUSER_ID, vals)
            order.write({'procurement_group_id': group_id})
        else:
            group_id = order.procurement_group_id.id
        vals = so_obj._prepare_order_line_procurement(cr, SUPERUSER_ID, line.order_id, line, group_id=group_id)
        # Search related moves
        related_moves = sol_dict[line.id]
        vals.update({'move_ids': [(6, 0, related_moves)]})
        vals.update({'state': 'running'})
        proc_id = proc_obj.create(cr, SUPERUSER_ID, vals)
        proc_obj.check(cr, SUPERUSER_ID, [proc_id])
        move_obj.write(cr, SUPERUSER_ID, related_moves, {'group_id': group_id})