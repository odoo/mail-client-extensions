from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.osv import fields, osv



def migrate(cr, version):
    """
        For all sale orders that are not delivered yet, create procurements 
        to these lines
    """
    
    # Check all sale order lines where the sales order is not done and not shipped and not cancelled
    # and create procurements for it and add moves to them.   
    registry = RegistryManager.get(cr.dbname)
    move_obj = registry["stock.move"]
    sol_obj = registry['sale.order.line']
    proc_obj = registry['procurement.order']
    cr.execute("""SELECT sm.sale_line_id, sm.id FROM stock_move sm, sale_order_line sol, sale_order so, product_product pp, product_template pt WHERE so.shipped = False
    and so.state <> 'done' and so.state <> 'cancel' and pp.product_tmpl_id = pt.id
    and pt.type <> 'service' and pp.id = sol.product_id and so.id = sol.order_id and sm.sale_line_id = sol.id 
    """)
    sol_dict = {}
    for item in cr.fetchall():
        if not sol_dict.get(item[0]):
            sol_dict[item[0]] = [item[1]]
        else:
            sol_dict[item[0]] += [item[1]] 
    
    for line in sol_obj.browse(cr, SUPERUSER_ID, sol_dict.keys()):
        vals = registry['sale.order']._prepare_order_line_procurement(cr, SUPERUSER_ID, line.order_id, line)
        # Search related moves
        related_moves = sol_dict[line.id]
        vals.update({'move_ids': [(6, 0, related_moves)]})
        moves = move_obj.browse(cr, SUPERUSER_ID, related_moves)
        if all([x.state == 'done' for x in moves]):
            vals.update({'state': 'done'})
        else:
            vals.update({'state': 'running'})
        proc_id = proc_obj.create(cr, SUPERUSER_ID, vals)
