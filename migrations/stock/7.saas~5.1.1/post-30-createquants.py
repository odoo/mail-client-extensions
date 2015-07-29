import logging
import datetime

from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.stock.saas-5.'
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    """
        1 Get all stock moves ordered by execution date.  Find the correct quants and move them
        2 The in_date of the quant should be the first move done
        3 Moves that are assigned should be unassigned
        This should all be done with standard cost and no real-time valuation
        as we will assign these properties afterwards
    """
    registry = RegistryManager.get(cr.dbname)
    move_obj = registry['stock.move']
    quant_obj = registry['stock.quant']
    moves = move_obj.search(cr, SUPERUSER_ID, [('state', '=', 'done'),('product_qty', '>', 0.0)], order='date')
    t1 = datetime.datetime.now()
    t0 = t1
    for index, move in enumerate(util.iter_browse(move_obj, cr, SUPERUSER_ID,
                                                  moves)):
        quants = quant_obj.quants_get_prefered_domain(cr, SUPERUSER_ID, move.location_id, move.product_id, move.product_qty, domain=[('qty', '>', 0.0)], 
                                                      prefered_domain_list=[], restrict_lot_id=move.restrict_lot_id.id)
        quant_obj.quants_move(cr, SUPERUSER_ID, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id)
        t2 = datetime.datetime.now()
        if (t2 - t1).total_seconds() > 60:
            t1 = datetime.datetime.now()
            _logger.info(
                "[%.02f%%] %d/%d stock moves processed in %s "
                "(TOTAL estimated time: %s)",
                (float(index) / float(len(moves)) * 100.0),
                index, len(moves), (t2 - t0),
                datetime.timedelta(
                    seconds=((t2 - t0).total_seconds()
                             * float(len(moves)) / float(index))))
    
    #Take in_date as first date of stock_move
    cr.execute("""
    UPDATE stock_quant SET in_date = qdate.date 
    FROM
    (SELECT sq.id as id, MIN(sm.date) as date FROM stock_quant sq, stock_quant_move_rel sqmr, stock_move sm
    WHERE sq.id = sqmr.quant_id AND sm.id = sqmr.move_id AND sm.state = 'done' AND sm.date is not null GROUP BY sq.id) AS qdate
    WHERE stock_quant.id = qdate.id
    """)

    # Assigned moves should be reassigned to give them to appropriate quants
    moves = move_obj.search(cr, SUPERUSER_ID, [('state','=','assigned')])
    move_obj.write(cr, SUPERUSER_ID, moves, {'state': 'confirmed'})
    move_obj.action_assign(cr, SUPERUSER_ID, moves)