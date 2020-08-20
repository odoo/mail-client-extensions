import logging
import os

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
    if os.environ.get('ODOO_MIG_S5_SKIP_QUANTS_CREATION'):
        return

    registry = RegistryManager.get(cr.dbname)
    move_obj = registry['stock.move']
    quant_obj = registry['stock.quant']
    if os.environ.get('ODOO_MIG_S5_SQL_QUANTS_CREATION'):
        cr.execute(
            """
                INSERT INTO stock_quant(product_id, location_id, company_id, lot_id, qty, in_date)
                     SELECT product_id, location_id, company_id, lot_id, SUM(qty), MIN(date) FROM (

                          SELECT m.product_id, m.location_dest_id as location_id, m.company_id,
                                 m.restrict_lot_id as lot_id, m.product_qty as qty, m.date as date
                            FROM stock_move m
                            JOIN product_product pp ON pp.id = m.product_id
                            JOIN product_template pt ON pt.id = pp.product_tmpl_id
                           WHERE m.state = 'done'
                             AND pt.type != 'consu'

                        UNION ALL

                          SELECT m.product_id, m.location_id, m.company_id,
                                 m.restrict_lot_id as lot_id, -m.product_qty as qty, m.date as date
                            FROM stock_move m
                            JOIN stock_location l on l.id = m.location_id
                            JOIN product_product pp ON pp.id = m.product_id
                            JOIN product_template pt ON pt.id = pp.product_tmpl_id
                           WHERE m.state = 'done'
                             AND l.usage = 'internal'
                             AND pt.type != 'consu'

                     ) as quants
                GROUP BY product_id, location_id, company_id, lot_id
                  HAVING SUM(qty) != 0
            """
        )
    else:
        moves = move_obj.search(cr, SUPERUSER_ID, [('state', '=', 'done'), ('product_qty', '>', 0.0)], order='company_id, date')
        for move in util.iter_browse(move_obj, cr, SUPERUSER_ID, moves, logger=_logger):
            preferred_domain = []
            if move.move_orig_ids:
                preferred_domain = [[('history_ids', 'in', [x.id for x in move.move_orig_ids])], [('history_ids', 'not in', [x.id for x in move.move_orig_ids])]]
            quants = quant_obj.quants_get_prefered_domain(cr, SUPERUSER_ID, move.location_id, move.product_id, move.product_qty, domain=[('qty', '>', 0.0)],
                                                        prefered_domain_list=preferred_domain, restrict_lot_id=move.restrict_lot_id.id, context={'force_company': move.company_id.id})
            quant_obj.quants_move(cr, SUPERUSER_ID, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id)

        #Take in_date as first date of stock_move
        cr.execute("""
        UPDATE stock_quant SET in_date = qdate.date
        FROM
        (SELECT sq.id as id, MIN(sm.date) as date FROM stock_quant sq, stock_quant_move_rel sqmr, stock_move sm
        WHERE sq.id = sqmr.quant_id AND sm.id = sqmr.move_id AND sm.state = 'done' AND sm.date is not null GROUP BY sq.id) AS qdate
        WHERE stock_quant.id = qdate.id
        """)

    # Assigned moves should be reassigned to give them to appropriate quants
    moves = move_obj.search(cr, SUPERUSER_ID, [('state', '=', 'assigned')])
    move_obj.write(cr, SUPERUSER_ID, moves, {'state': 'confirmed'})
    move_obj.action_assign(cr, SUPERUSER_ID, moves)
