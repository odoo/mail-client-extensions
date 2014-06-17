from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Get all stock moves ordered by execution date.  Find the correct quants and move them
    """
    print "*********** CREATE QUANTS ******************"
    registry = RegistryManager.get(cr.dbname)
    move_obj = registry['stock.move']
    quant_obj = registry['stock.quant']
    moves = move_obj.search(cr, SUPERUSER_ID, [('state', '=', 'done')], order='date')
    for move in move_obj.browse(cr, SUPERUSER_ID, moves):
        quants = quant_obj.quants_get_prefered_domain(cr, SUPERUSER_ID, move.location_id, move.product_id, move.product_qty, domain=[('qty', '>', 0.0)], 
                                                      prefered_domain_list=[], restrict_lot_id=move.restrict_lot_id.id)
        quant_obj.quants_move(cr, SUPERUSER_ID, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id)