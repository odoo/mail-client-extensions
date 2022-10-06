import datetime
import logging
import os
from itertools import groupby
from operator import itemgetter

from openerp import SUPERUSER_ID
from openerp.addons.base.maintenance.migrations import util
from openerp.osv import osv

from openerp.tools import float_round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare

refresh_dict = {'quant': 'stock_quant',
                'move': 'stock_move'}

NS = 'openerp.addons.base.maintenance.migrations.stock.saas-5.'
_logger = logging.getLogger(NS + __name__)


class Global(object):
    moves_by_id = None
    moves_by_dest_id = None
    locations_by_id = None
    products_by_id = None
    company_by_user = None
    rounding_by_product_id = None
    property_by_tmpl_id = None
    stock_move_operation_link_by_move_id = None
    stock_move_operation_link_by_operation_id = None

self = Global()


def group(lst, cols):
    if isinstance(cols, basestring):
        cols = [cols]
    return dict((k, [v for v in itr]) for k, itr in groupby(
        sorted(lst, key=itemgetter(*cols)), itemgetter(*cols)))


def get_reserved_availability(cr, move):
    cr.execute("""
        SELECT qty
        FROM stock_quant
        WHERE reservation_id = %s
    """, [move['id']])
    quantities = [r[0] for r in cr.fetchall()]
    return sum(quantities) if quantities else 0


def migrate(cr, version):
    if os.environ.get('ODOO_MIG_S5_SKIP_QUANTS_CREATION'):
        _migrate(cr, version)


def _migrate(cr, version):
    """
        1 Get all stock moves ordered by execution date.  Find the correct quants and move them
        2 The in_date of the quant should be the first move done
        3 Moves that are assigned should be unassigned
        This should all be done with standard cost and no real-time valuation
        as we will assign these properties afterwards
    """
    if not util.column_exists(cr, 'stock_pack_operation', 'from_move_id'):
        cr.execute("""
            ALTER TABLE stock_pack_operation ADD COLUMN from_move_id integer
        """)

    if os.environ.get('ODOO_MIG_S5_MIGRATE_QUANTS_WITH_PACKAGES'):
        migrate_packages(cr)

    cr.execute("""
        SELECT id, date, move_dest_id, location_id, product_id, location_dest_id, product_qty,
               restrict_lot_id, restrict_partner_id, company_id, partially_available,
               state, origin_returned_move_id, picking_id, price_unit
        FROM stock_move
    """)

    all_moves = cr.dictfetchall()

    self.moves_by_id = dict([(r['id'], r) for r in all_moves])
    self.moves_by_dest_id = group(all_moves, 'move_dest_id')

    cr.execute("""
        SELECT id, name, usage, parent_left, parent_right
        FROM stock_location
    """)
    self.locations_by_id = dict([(r['id'], r) for r in cr.dictfetchall()])

    cr.execute("""
        SELECT id, product_tmpl_id
        FROM product_product
    """)
    self.products_by_id = dict([(r['id'], r) for r in cr.dictfetchall()])

    cr.execute("""select id, company_id from res_users""")
    self.company_by_user = dict([(r[0], r[1]) for r in cr.fetchall()])

    cr.execute("""
        SELECT pp.id,
               uom.rounding
        FROM product_uom uom,
             product_product pp,
             product_template pt
        WHERE pp.product_tmpl_id = pt.id
          AND pt.uom_id = uom.id
    """)
    self.rounding_by_product_id = dict([(r[0], r[1]) for r in cr.fetchall()])

    cr.execute("""
        SELECT id, product_id, owner_id, lot_id, package_id, result_package_id, from_move_id
        FROM stock_pack_operation
    """)
    all_operations = cr.dictfetchall()
    self.operations_by_move_id = group(all_operations, 'from_move_id')

    cr.execute("""
        SELECT id
        FROM stock_quant_package
    """)
    self.packages_by_id = dict([(r['id'], r) for r in cr.dictfetchall()])

    self.recursive_child_id = {}
    self.recursive_package_child_id = {}

    cr.execute("""
        SELECT split_part(p.res_id, ',', 2)::int,
               p.value_float
        FROM ir_property p
        WHERE split_part(res_id,',',1) = 'product.template'
          AND p.value_float IS NOT NULL
    """)
    self.property_by_tmpl_id = dict([(r[0], r[1]) for r in cr.fetchall()])

    cr.execute("""
        SELECT id, move_id, operation_id
        FROM stock_move_operation_link
    """)
    stock_move_operation_links = cr.dictfetchall()
    self.stock_move_operation_link_by_move_id = group(stock_move_operation_links, 'move_id')
    self.stock_move_operation_link_by_operation_id = group(
        stock_move_operation_links, 'operation_id')

    cr.execute("""
        SELECT value
        FROM ir_config_parameter
        WHERE KEY = 'migration.stock_with_packs.last_stock_move_id'
    """)
    res = cr.fetchone()
    LAST_STOCK_MOVE_ID = None
    if res:
        LAST_STOCK_MOVE_ID = res[0]

    if not LAST_STOCK_MOVE_ID:
        cr.execute("""
            SELECT id, date, location_id, product_id, location_dest_id, product_qty,
                   restrict_lot_id, restrict_partner_id, company_id, partially_available, state,
                   origin_returned_move_id, picking_id, price_unit
            FROM stock_move
            WHERE state = 'done'
              AND product_qty > 0.0
            ORDER BY company_id, date
        """)
        moves = cr.dictfetchall()
    else:
        cr.execute("""
            SELECT id, date, location_id, product_id, location_dest_id, product_qty,
                   restrict_lot_id, restrict_partner_id, company_id, partially_available,
                   state, origin_returned_move_id, picking_id, price_unit
            FROM stock_move
            WHERE state = 'done'
              AND product_qty > 0.0
              AND id > %s
            ORDER BY company_id, date
        """, [int(LAST_STOCK_MOVE_ID)])
        moves = cr.dictfetchall()

    chunk_size = 200
    size = (len(moves) + chunk_size - 1) / chunk_size
    qual = 'chunks of %s stock.move records' % chunk_size
    _logger.info("START_QUANTS")
    for chunk in util.log_progress(
        util.chunks(moves, chunk_size, list),
        qualifier=qual, logger=_logger, size=size):
        preferred_domain = []
        preferred_domain = []
        for move in chunk:
            context = {}
            ops = self.operations_by_move_id.get(move['id'], {})
            package, result_package = [None, None]
            if ops:
                op = ops[0]
                package = self.packages_by_id[op['package_id']] if op['package_id'] else None
                result_package = self.packages_by_id[op['result_package_id']] \
                    if op['result_package_id'] \
                    else None

            move['reserved_availability'] = get_reserved_availability(cr, move)

            move_orig_ids = [r['id'] for r in self.moves_by_dest_id.get(move['id'], [])]
            if move_orig_ids:
                list_of_ids = ', '.join([str(id) for id in move_orig_ids])
                preferred_domain = [
                    ' and id in (select quant_id from stock_quant_move_rel where move_id in (%s))' % (list_of_ids, ),
                    ' and id not in (select quant_id from stock_quant_move_rel where move_id in (%s))' % (list_of_ids, )]

            location = self.locations_by_id[move['location_id']]
            product = self.products_by_id[move['product_id']]
            location_dest = self.locations_by_id[move['location_dest_id']]

            quants = quants_get_prefered_domain(
                cr, SUPERUSER_ID, location, product, move['product_qty'], domain='qty > 0.0',
                prefered_domain_list=preferred_domain, restrict_lot_id=move['restrict_lot_id'],
                context={'force_company': move['company_id']})
            quants_move(
                cr, SUPERUSER_ID, quants, move, location_dest, lot_id=move['restrict_lot_id'],
                src_package_id=package['id'] if package else None,
                dest_package_id=result_package['id'] if result_package else None, context=context)
        cr.execute('commit')
        cr.execute('begin')

    #Take in_date as first date of stock_move
    cr.execute("""
        UPDATE stock_quant
        SET in_date = qdate.date
        FROM
          (SELECT sq.id AS id,
                  MIN(sm.date) AS date
           FROM stock_quant sq,
                stock_quant_move_rel sqmr,
                stock_move sm
           WHERE sq.id = sqmr.quant_id
             AND sm.id = sqmr.move_id
             AND sm.state = 'done'
             AND sm.date IS NOT NULL
           GROUP BY sq.id) AS qdate
        WHERE stock_quant.id = qdate.id
    """)

    # Assigned moves should be reassigned to give them to appropriate quants
    cr.execute("""
        UPDATE stock_move
        SET STATE = 'confirmed'
        WHERE STATE = 'assigned' returning *
    """)
    moves = cr.dictfetchall()
    # recompute their stock_picking state:
    recompute_stock_picking_state(cr, moves)
    action_assign(cr, SUPERUSER_ID, moves)

def recompute_stock_picking_state(cr, moves):
    # select id from stock_picking p where not exists (select 1 from stock_move m where p.id=m.picking_id);
    pass

def quants_get_prefered_domain(cr, uid, location, product, qty, domain=None, prefered_domain_list=[], restrict_lot_id=False, restrict_partner_id=False, context=None):
    ''' This function tries to find quants in the given location for the given domain, by trying
        to first limit the choice on the quants that match the first item of prefered_domain_list
        as well. But if the qty requested is not reached it tries to find the remaining quantity
        by looping on the prefered_domain_list (tries with the second item and so on).
        Make sure the quants aren't found twice => all the domains of prefered_domain_list should
        be orthogonal
    '''
    if domain is None:
        domain = []
    quants = [(None, qty)]
    #don't look for quants in location that are of type production, supplier or inventory.
    if location['usage'] in ['inventory', 'production', 'supplier']:
        return quants
    res_qty = qty
    if not prefered_domain_list:
        return quants_get(
            cr, uid, location, product, qty, domain=domain, restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id, context=context)
    for prefered_domain in prefered_domain_list:
        res_qty_cmp = float_compare(res_qty, 0, precision_rounding=get_rounding(cr, product['id']))
        if res_qty_cmp > 0:
            # try to replace the last tuple (None, res_qty) with something that wasn't chosen at
            # first because of the prefered order
            quants.pop()
            tmp_quants = quants_get(
                cr, uid, location, product, res_qty, domain=domain + prefered_domain,
                restrict_lot_id=restrict_lot_id, restrict_partner_id=restrict_partner_id,
                context=context)
            for quant in tmp_quants:
                if quant[0]:
                    res_qty -= quant[1]
            quants += tmp_quants
    return quants

def quants_get(cr, uid, location, product, qty, domain=None, restrict_lot_id=False,
               restrict_partner_id=False, context=None):
    """
    Use the removal strategies of product to search for the correct quants
    If you inherit, put the super at the end of your method.

    :location: browse record of the parent location where the quants have to be found
    :product: browse record of the product to find
    :qty in UoM of product
    """
    result = []
    domain = domain or 'qty > 0.0'
    if restrict_partner_id:
        domain += ' and owner_id = ' + str(restrict_partner_id)
    if restrict_lot_id:
        domain += ' and lot_id = ' + str(restrict_lot_id)
    if location:
        removal_strategy = 'fifo'
        result += apply_removal_strategy(
            cr, uid, location, product, qty, domain, removal_strategy, context=context)
    return result

def apply_removal_strategy(cr, uid, location, product, quantity, domain, removal_strategy,
                           context=None):
    if removal_strategy == 'fifo':
        order = 'in_date, id'
        return _quants_get_order(
            cr, uid, location, product, quantity, domain, order, context=context)
    elif removal_strategy == 'lifo':
        order = 'in_date desc, id desc'
        return _quants_get_order(
            cr, uid, location, product, quantity, domain, order, context=context)
    raise osv.except_osv(
        'Error!', 'Removal strategy %s not implemented.' % (removal_strategy,))

def _quants_get_order(cr, uid, location, product, quantity, domain=[], orderby='in_date',
                      context=None):
    ''' Implementation of removal strategies
        If it can not reserve, it will return a tuple (None, qty)
    '''
    if location:
        domain += recursive_child_id(cr, location['id'])
    domain += ' and product_id = ' + str(product['id'])
    if context.get('force_company'):
        domain += ' and company_id = ' + str(context.get('force_company'))
    else:
        company_id = self.company_by_user[SUPERUSER_ID]
        domain += ' and company_id = ' + str(company_id)
    res = []
    #offset = 0
    prec_round = get_rounding(cr, product['id'])
    while float_compare(quantity, 0, precision_rounding=prec_round) > 0:
        cr.execute("""
            SELECT *
            FROM stock_quant
            WHERE %s
            ORDER BY %s
        """ % (domain, orderby))
        quants = cr.dictfetchall()
        if not quants:
            res.append((None, quantity))
            break
        for quant in quants:
            rounding = prec_round
            if float_compare(quantity, abs(quant['qty']), precision_rounding=rounding) >= 0:
                res += [(quant, abs(quant['qty']))]
                quantity -= abs(quant['qty'])
            elif float_compare(quantity, 0.0, precision_rounding=rounding) != 0:
                res += [(quant, quantity)]
                quantity = 0
                break
        #offset += 10
    return res

###END: Converting all methods needed for quants_get_prefered_domain()


###START: Converting all methods needed for quants_move()

def quants_move(cr, uid, quants, move, location_to, location_from=False, lot_id=False,
                owner_id=False, src_package_id=False, dest_package_id=False, context=None):
    """Moves all given stock.quant in the given destination location.  Unreserve from current move.
    :param quants: list of tuple(browse record(stock.quant) or None, quantity to move)
    :param move: browse record (stock.move)
    :param location_to: browse record (stock.location) depicting where the quants have to be moved
    :param location_from: optional browse record (stock.location) explaining where the quant has
           to be taken (may differ from the move source location in case a removal strategy
           applied). This parameter is only used to pass to _quant_create if a negative quant
           must be created
    :param lot_id: ID of the lot that must be set on the quants to move
    :param owner_id: ID of the partner that must own the quants to move
    :param src_package_id: ID of the package that contains the quants to move
    :param dest_package_id: ID of the package that must be set on the moved quant
    """
    quants_reconcile = []
    to_move_quants = []
    _check_location(cr, uid, location_to, context=context)
    for quant, qty in quants:
        if not quant:
            # If quant is None, we will create a quant to move (and potentially a negative
            # counterpart too)
            quant = _quant_create(
                cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id,
                src_package_id=src_package_id, dest_package_id=dest_package_id,
                force_location_from=location_from, force_location_to=location_to, context=context)
        else:
            _quant_split(cr, uid, quant, qty, context=context)
            to_move_quants.append(quant)
        quants_reconcile.append(quant)
    if to_move_quants:
        to_recompute_move_ids = [
            x['reservation_id'] for x in to_move_quants
                if x['reservation_id'] and x['reservation_id'] != move['id']]
        move_quants_write(
            cr, uid, to_move_quants, move, location_to, dest_package_id, context=context)
        if to_recompute_move_ids:
            recalculate_move_state(cr, uid, to_recompute_move_ids, context=context)
    if location_to['usage'] == 'internal':
        # Do manual search for quant to avoid full table scan (order by id)
        cr.execute("""
            SELECT 0
            FROM stock_quant,
                 stock_location
            WHERE product_id = %s
              AND stock_location.id = stock_quant.location_id
              AND ((stock_location.parent_left >= %s
                    AND stock_location.parent_left < %s)
                   OR stock_location.id = %s)
              AND qty < 0.0 LIMIT 1
        """, [move['product_id'], location_to['parent_left'], location_to['parent_right'],
              location_to['id']])
        if cr.fetchone():
            for quant in quants_reconcile:
                _quant_reconcile_negative(cr, uid, quant, move, context=context)

def _check_location(cr, uid, location, context=None):
    if location['usage'] == 'view':
        raise osv.except_osv(
            'Error', 'You cannot move to a location of type view %s.') % (location['name'])
    return True

def _quant_create(cr, uid, qty, move, lot_id=False, owner_id=False, src_package_id=False,
                  dest_package_id=False, force_location_from=False, force_location_to=False,
                  context=None):
    '''Create a quant in the destination location and create a negative quant in the source
       location if it's an internal location.
    '''
    if context is None:
        context = {}
    price_unit = get_price_unit(cr, uid, move, context=context)
    location = force_location_to or move['location_dest_id']
    rounding = get_rounding(cr, move['product_id'])
    vals = {
        'product_id': move['product_id'],
        'location_id': location['id'],
        'qty': float_round(qty, precision_rounding=rounding),
        'cost': price_unit,
        'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'company_id': move['company_id'],
        'lot_id': lot_id or None,
        'owner_id': owner_id or None,
        'package_id': dest_package_id or None,
    }
    location = self.locations_by_id[move['location_id']]
    #usage, = cr.fetchone()
    usage = location['usage']
    package_id = None
    if usage == 'internal':
        # if we were trying to move something from an internal location and
        # reach here (quant creation),
        # it means that a negative quant has to be created as well.
        negative_vals = vals.copy()
        negative_vals['location_id'] = force_location_from or move['location_id']
        negative_vals['qty'] = float_round(-qty, precision_rounding=rounding)
        negative_vals['cost'] = price_unit
        negative_vals['negative_move_id'] = move['id']
        if negative_vals.get('package_id'):
            if isinstance(negative_vals.get('package_id'), (int, long)):
                package_id = negative_vals.get('package_id')

        cr.execute("""
            INSERT INTO stock_quant (
                product_id, location_id, qty, cost, in_date, company_id, lot_id, owner_id,
                package_id, negative_move_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
            ) returning id
        """, [negative_vals['product_id'], negative_vals['location_id'], negative_vals['qty'],
              negative_vals['cost'], negative_vals['in_date'], negative_vals['company_id'],
              negative_vals['lot_id'], negative_vals['owner_id'], package_id,
              negative_vals['negative_move_id']])
        negative_quant_id, = cr.fetchone()
        insert_stock_quant_move_rel(cr, negative_quant_id, move['id'])
        vals.update({'propagated_from_id': negative_quant_id})

    # create the quant as superuser, because we want to restrict the creation of quant manually:
    # we should always use this method to create quants
    cr.execute("""
        INSERT INTO stock_quant (
            product_id, location_id, qty, cost, in_date, company_id, lot_id, owner_id,
            package_id, propagated_from_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s
        ) returning id
    """, [vals['product_id'], vals['location_id'], vals['qty'], vals['cost'], vals['in_date'],
          vals['company_id'], vals['lot_id'], vals['owner_id'], package_id,
          vals.get('propagated_from_id', None), ])
    quant_id, = cr.fetchone()
    insert_stock_quant_move_rel(cr, quant_id, move['id'])
    cr.execute("select * from stock_quant where id = %s", [quant_id, ])
    return cr.dictfetchone()

def _quant_split(cr, uid, quant, qty, context=None):
    context = context or {}
    rounding = get_rounding(cr, quant['product_id'])
    if float_compare(abs(quant['qty']), abs(qty), precision_rounding=rounding) <= 0:
        # if quant <= qty in abs, take it entirely
        return False
    # Fetch the history_ids manually as it will not do a join with the stock moves then
    # (=> a lot faster)
    cr.execute("""
        SELECT move_id FROM stock_quant_move_rel WHERE quant_id = %s
    """, (quant['id'],))
    res = cr.fetchall()
    cr.execute("""
        INSERT INTO stock_quant (product_id, location_id, qty, company_id,cost, in_date)
        SELECT product_id, location_id, (%s - %s) AS qty, company_id, cost, in_date
        FROM stock_quant
        WHERE id = %s RETURNING *
    """, [quant['qty'], qty, quant['id']])
    new_quant = cr.dictfetchone()
    move_id = res[0]
    insert_stock_quant_move_rel(cr, new_quant['id'], move_id)
    cr.execute("""update stock_quant set qty=%s where id=%s""",[qty, quant['id']])
    quant['qty'] = qty
    return new_quant

def move_quants_write(cr, uid, quants, move, location_dest_id, dest_package_id, context=None):
    context=context or {}
    if not context.get('entire_pack') and dest_package_id:
        package_id = dest_package_id
    else:
        package_id = None
    for quant in quants:
        cr.execute("""
            UPDATE stock_quant
            SET location_id = %s,
                package_id = %s
            WHERE id = %s
        """, [location_dest_id['id'], package_id, quant['id']])
        insert_stock_quant_move_rel(cr, quant['id'], move['id'])

def recalculate_move_state(cr, uid, move_ids, context=None):
    '''Recompute the state of moves given because their reserved quants were used to fulfill
       another operation'''
    recalculate_moves = [self.moves_by_id[move_id] for move_id in move_ids]
    for move in recalculate_moves:
        vals = {}
        cr.execute("""
            SELECT id
            FROM stock_quant
            WHERE reservation_id = %s
        """, [move['id']])
        reserved_quant_ids = cr.fetchall()
        if len(reserved_quant_ids) > 0 and not move['partially_available']:
            vals['partially_available'] = True
        if len(reserved_quant_ids) == 0 and move['partially_available']:
            vals['partially_available'] = False
        if move['state'] == 'assigned':
            if find_move_ancestors(cr, uid, move, context=context):
                vals['state'] = 'waiting'
            else:
                vals['state'] = 'confirmed'
        if vals:
            cr.execute("""
                UPDATE stock_move
                SET partially_available = %s,
                    state = %s
                WHERE id = %s
            """,[vals.get('partially_available'), vals.get('state'), move.get('id')])

def find_move_ancestors(cr, uid, move, context=None):
    '''Find the first level ancestors of given move '''
    ancestors = []
    move2 = move
    while move2:
        move_orig_id = self.moves_by_id[move2['id']]
        ancestors += [move_orig_id['id']]
        # loop on the split_from to find the ancestor of split moves only if the move has not
        # direct ancestor (priority goes to them)
        move2 = not move_orig_id and move2['split_from'] or False
    return ancestors

def _quant_reconcile_negative(cr, uid, quant, move, context=None):
    """
        When new quant arrive in a location, try to reconcile it with
        negative quants. If it's possible, apply the cost of the new
        quant to the conter-part of the negative quant.
    """
    # Force read quant data from database. Do not depend on values in python object.
    cr.execute("""
        SELECT *
        FROM stock_quant
        WHERE id = %s
    """, [quant['id'], ])
    quant = cr.dictfetchone()
    if not quant:
        return
    context = context or {}
    context = dict(context)
    context.update({'force_unlink': True})
    solving_quant = quant

    dom = 'qty < 0'
    if quant['lot_id']:
        dom += ' and lot_id = ' + str(quant['lot_id'])
    if quant['owner_id']:
        dom += ' and owner_id = ' + str(quant['owner_id'])
    if quant['package_id']:
        dom += ' and package_id = ' + str(quant['package_id'])
    if quant['propagated_from_id']:
        dom += ' and id != ' + str(quant['propagated_from_id'])
    location = self.locations_by_id[quant['location_id']]
    product = self.products_by_id[quant['product_id']]
    quants = quants_get(cr, uid, location, product, quant['qty'], dom, context=context)
    product_uom_rounding = get_rounding(cr, quant['product_id'])

    for quant_neg, qty in quants:
        if not quant_neg or not solving_quant:
            continue
        cr.execute("""
            SELECT id
            FROM stock_quant
            WHERE propagated_from_id = %s
        """, [quant_neg['id'], ])
        to_solve_quant_ids = cr.fetchall()
        if not to_solve_quant_ids:
            continue
        solving_qty = qty
        solved_quant_ids = []
        cr.execute("""
            SELECT *
            FROM stock_quant
            WHERE id IN %s
        """, [tuple(x for x in to_solve_quant_ids), ])
        to_solve_quants = cr.dictfetchall()
        for to_solve_quant in to_solve_quants:
            if float_compare(solving_qty, 0, precision_rounding=product_uom_rounding) <= 0:
                continue
            solved_quant_ids.append(to_solve_quant['id'])
            _quant_split(
                cr, uid, to_solve_quant, min(solving_qty, to_solve_quant['qty']), context=context)
            solving_qty -= min(solving_qty, to_solve_quant['qty'])
        remaining_solving_quant = _quant_split(cr, uid, solving_quant, qty, context=context)
        remaining_neg_quant = _quant_split(cr, uid, quant_neg, -qty, context=context)
        #if the reconciliation was not complete, we need to link together the remaining parts
        if remaining_neg_quant:
            cr.execute("""
                SELECT id
                FROM stock_quant
                WHERE propagated_from_id = %s
                  AND id NOT IN %s
            """, [quant_neg['id'], tuple(solved_quant_ids), ])
            remaining_to_solve_quant_ids = cr.fetchall()
            if remaining_to_solve_quant_ids:
                cr.execute("""
                    UPDATE stock_quant
                    SET propagated_from_id = %s
                    WHERE id IN %s
                """, [remaining_neg_quant['id'], tuple(remaining_to_solve_quant_ids), ])
        #TO FIX: the below causes a problem. But it wasn't there in old script.
        if solving_quant['propagated_from_id'] and solved_quant_ids: #not covered by old script
            cr.execute("""
                UPDATE stock_quant
                SET propagated_from_id = %s
                WHERE id IN %s
            """, [solving_quant['propagated_from_id'], tuple(solved_quant_ids), ])
        #delete the reconciled quants, as it is replaced by the solved quants
        cr.execute("""
            DELETE
            FROM stock_quant
            WHERE id = %s
        """, [quant_neg['id'], ])
        cr.execute("""
            DELETE
            FROM stock_quant_move_rel
            WHERE quant_id = %s
        """, [quant_neg['id'], ]) #not covered by old script
        if solved_quant_ids:
            #price update + accounting entries adjustments
            cr.execute("""
                UPDATE stock_quant
                SET cost = %s
                WHERE id IN %s
            """ , (solving_quant['cost'], tuple(solved_quant_ids),))
            #merge history (and cost?)
            _quants_merge(cr, uid, solved_quant_ids, solving_quant, context=context)
        cr.execute("""
            DELETE
            FROM stock_quant
            WHERE id = %s
        """, [solving_quant['id'], ])
        solving_quant = remaining_solving_quant

def _quants_merge(cr, uid, solved_quant_ids, solving_quant, context=None):
    cr.execute("""
        SELECT move_id
        FROM stock_quant_move_rel
        WHERE quant_id = %s
    """, [solving_quant['id'], ])
    moves =  cr.fetchall()
    for solved_quant in solved_quant_ids:
        for move_id in moves:
            insert_stock_quant_move_rel(cr, solved_quant, move_id)

###END: Converting all methods needed for quants_move()


###START: Converting all methods needed for action_assign()

def action_assign(cr, uid, moves, context=None):
    """ Checks the product type and accordingly writes the state.
    """
    context = context or {}
    to_assign_moves = set()
    main_domain = {}
    todo_moves = []
    operations = set()
    for move in moves:
        if move['state'] not in ('confirmed', 'waiting', 'assigned'):
            continue
        location = self.locations_by_id[move['location_id']]
        usage = location['usage']
        if usage in ('supplier', 'inventory', 'production'):
            to_assign_moves.add(move['id'])
            # in case the move is returned, we want to try to find quants before forcing the
            # assignment
            if not move['origin_returned_move_id']:
                continue
        cr.execute("""
            SELECT TYPE
            FROM product_template
            WHERE id =
                (SELECT product_tmpl_id
                 FROM product_product
                 WHERE id = %s)
        """, [move['product_id'], ])
        product_type, = cr.fetchone()
        if product_type == 'consu':
            to_assign_moves.add(move['id'])
            continue
        else:
            todo_moves.append(move)

            # we always keep the quants already assigned and try to find the remaining quantity
            # on quants not assigned only
            main_domain[move['id']] = 'reservation_id IS NULL and qty > 0'

            # if the move is preceeded, restrict the choice of quants in the ones moved
            # previously in original move
            ancestors = find_move_ancestors(cr, uid, move, context=context)
            if move['state'] == 'waiting' and not ancestors:
                # if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't
                # find any quant available in stock
                main_domain[move['id']] += ' and id = False'
            elif ancestors:
                main_domain[move['id']] += ' and id in (select quant_id from stock_quant_move_rel where move_id in ({}))'.format(', '.join(map(str, ancestors)))

            #if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
            if move['origin_returned_move_id']:
                main_domain[move['id']] += ' and id in (select quant_id from stock_quant_move_rel where move_id = '+ str(move['origin_returned_move_id']) + ')'
            linked_move_operation_ids = self.stock_move_operation_link_by_move_id.get(move['id'], [])
            for link in linked_move_operation_ids:
                operations.add(link['operation_id'])
    # Check all ops and sort them: we want to process first the packages, then operations
    # with lot then the rest
    operations = list(operations)
    operations.sort(
        key=lambda x: ((x['package_id'] and not x['product_id']) and -4 or 0) + (x['package_id'] and -2 or 0) + (x['lot_id'] and -1 or 0))
    for ops in operations:
        #first try to find quants based on specific domains given by linked operations
        linked_move_operation_ids = self.stock_move_operation_link_by_operation_id.get(ops['id'], [])
        for record in linked_move_operation_ids:
            move = record['move_id']
            if move['id'] in main_domain:
                domain = main_domain[move['id']] + get_specific_domain(
                    cr, uid, record, context=context)
                qty = record['qty']
                if qty:
                    location = self.locations_by_id[ops['location_id']]
                    product = self.products_by_id[move['product_id']]

                    quants = quants_get_prefered_domain(
                        cr, uid, location, product, qty, domain=domain, prefered_domain_list=[],
                        restrict_lot_id=move['restrict_lot_id'],
                        restrict_partner_id=move['restrict_partner_id'], context=context)
                    quants_reserve(cr, uid, quants, move, record, context=context)
    for move in todo_moves:
        #then if the move isn't totally assigned, try to find quants without any specific domain
        if move['state'] != 'assigned':
            if not 'reserved_availability' in move:
                move['reserved_availability'] = get_reserved_availability(cr, move)
            qty_already_assigned = move['reserved_availability']
            qty = move['product_qty'] - qty_already_assigned

            location = self.locations_by_id[move['location_id']]
            product = self.products_by_id[move['product_id']]

            quants = quants_get_prefered_domain(
                cr, uid, location, product, qty, domain=main_domain[move['id']],
                prefered_domain_list=[], restrict_lot_id=move['restrict_lot_id'],
                restrict_partner_id=move['restrict_partner_id'], context=context)
            quants_reserve(cr, uid, quants, move, context=context)

    #force assignation of consumable products and incoming from supplier/inventory/production
    if to_assign_moves:
        force_assign(cr, uid, list(to_assign_moves), context=context)
    _state_get(cr)

def _state_get(cr):
    # set the state of picking according to Odoo8 method '_state_get'
    cr.execute("""
        SELECT id,
               move_type
        FROM stock_picking
    """)
    all_picking = cr.dictfetchall()
    res = {}
    total = len(all_picking)
    c = 0
    for p in all_picking:
        c += 1
        if not c % 1000:
            msg = "_state_get: {}/{}".format(c, total)
            _logger.info(msg)
        cr.execute("""
            SELECT id,
                   picking_id,
                   partially_available,
                   state
            FROM stock_move
            WHERE picking_id = %s
        """,[p['id']])
        all_move = cr.dictfetchall()
        state_group = ([(i['state']) for i in all_move])
        if any([x == 'draft' for x in state_group]):
            res[p['id']] = 'draft'
            continue
        if all([x == 'cancel' for x in state_group]):
            res[p['id']] = 'cancel'
            continue
        if all([x in ('cancel','done') for x in state_group]):
            res[p['id']] = 'done'
            continue
        order = {'confirmed': 0, 'waiting': 1, 'assigned': 2}
        order_inv = {0: 'confirmed', 1: 'waiting', 2: 'assigned'}
        lst = [order[x['state']] for x in all_move if x['state'] not in ('cancel', 'done')]
        if p['move_type'] == 'one':
            res[p['id']] = order_inv[min(lst)]
        else:
            res[p['id']] = order_inv[max(lst)]
            if not all(x == 2 for x in lst):
                if any(x == 2 for x in lst):
                    res[p['id']] = 'partially_available'
            else:
                for move in all_move:
                    if move['partially_available']:
                        res[p['id']] = 'partially_available'
                        break

    cr.execute("""
        SELECT id
        FROM stock_picking
        WHERE id NOT IN
            (SELECT picking_id
             FROM stock_move
             WHERE picking_id IS NOT NULL)
    """)
    picking_no_move = cr.dictfetchall()
    for x in picking_no_move:
        res[x['id']] = 'draft'
        continue

    for picking_id, state in res.items():
        cr.execute("""
            UPDATE stock_picking
            SET state = %s
            WHERE id = %s
        """,[state,picking_id])

def force_assign(cr, uid, ids, context=None):
    cr.execute("""
        UPDATE stock_move
        SET state = 'assigned'
        WHERE id IN %s
    """,
        [tuple(ids)])

def get_specific_domain(cr, uid, record, context=None):
    '''Returns the specific domain to consider for quant selection in action_assign() or
       action_done() of stock.move, having the record given as parameter making the link
       between the stock move and a pack operation'''

    op = record['operation_id']
    domain = []
    if op['package_id'] and op['product_id']:
        #if removing a product from a box, we restrict the choice of quants to this box
        domain += ' and package_id = ' + str(op['package_id'])
    elif op['package_id']:
        #if moving a box, we allow to take everything from inside boxes as well
        # XXX '=' or '+='?
        domain = recursive_package_child_id(cr, op['package_id'])
    else:
        #if not given any information about package, we don't open boxes
        domain += ' and package_id = False'
    #if lot info is given, we restrict choice to this lot otherwise we can take any
    if op['lot_id']:
        domain += ' and lot_id = ' + str(op['lot_id'])
    #if owner info is given, we restrict to this owner otherwise we restrict to no owner
    if op['owner_id']:
        domain += ' and owner_id = ' + str(op['owner_id'])
    else:
        domain += ' and owner_id = False'
    return domain

def quants_reserve(cr, uid, quants, move, link=False, context=None):
    '''This function reserves quants for the given move (and optionally given link). If the total
       of quantity reserved is enough, the move's state
       is also set to 'assigned'

       :param quants: list of tuple(quant browse record or None, qty to reserve). If None is
                      given as first tuple element, the item will be ignored. Negative quants
                      should not be received as argument
       :param move: browse record
       :param link: browse record (stock.move.operation.link)
    '''
    toreserve = []
    reserved_availability = move['reserved_availability']
    #split quants if needed
    for quant, qty in quants:
        if qty <= 0.0 or (quant and quant['qty'] <= 0.0):
            raise osv.except_osv(
                'Error!', 'You can not reserve a negative quantity or a negative quant.')
        if not quant:
            continue
        _quant_split(cr, uid, quant, qty, context=context)
        toreserve.append(quant['id'])
        reserved_availability += quant['qty']
    #reserve quants
    if toreserve:
        cr.execute("""
            UPDATE stock_quant
            SET reservation_id = %s
            WHERE id IN %s
        """, [move['id'], tuple(toreserve), ])
        # if move has a picking_id, write on that picking that pack_operation might have
        # changed and need to be recomputed
        if move['picking_id']:
            cr.execute("""
                UPDATE stock_picking
                SET recompute_pack_op = 't'
                WHERE id = %s
            """, [move['picking_id'], ])
    #check if move'state needs to be set as 'assigned'
    rounding = get_rounding(cr, move['product_id'])
    if float_compare(reserved_availability, move['product_qty'], precision_rounding=rounding) == 0 and move['state'] in ('confirmed', 'waiting')  :
        cr.execute("""
            UPDATE stock_move
            SET state = 'assigned'
            WHERE id = %s
        """, [move['id'], ])
    elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move['partially_available']:
        cr.execute("""
            UPDATE stock_move
            SET partially_available = 't'
            WHERE id = %s
        """, [move['id'], ])

###END: Converting all methods needed for action_assign()


###SMALL METHODS - for faster calculation
def get_price_unit(cr, uid, move, context=None):
    """ Returns the unit price to store on the quant """

    product = self.products_by_id[move['product_id']]
    return move['price_unit'] or self.property_by_tmpl_id.get(product['product_tmpl_id'])

def get_rounding(cr, product_id):
    return self.rounding_by_product_id[product_id]

def insert_stock_quant_move_rel(cr, quant_id, move_id):
    cr.execute(
        """
        INSERT INTO stock_quant_move_rel (quant_id, move_id)
             VALUES (%(quant_id)s, %(move_id)s)
        ON CONFLICT DO NOTHING
        """,
        locals(),
    )

def recursive_child_id(cr, location_id):
    res = self.recursive_child_id.get(location_id)
    if res is not None:
        return res

    cr.execute("""
         WITH RECURSIVE child_search(id) AS
          (SELECT id
           FROM stock_location
           WHERE id={id}
           UNION ALL SELECT sl.id
           FROM stock_location sl,
                               child_search p
           WHERE sl.location_id=p.id)
        SELECT *
        FROM child_search
    """.format(id = location_id))
    loc_id = cr.fetchall()
    child_ids = ''
    if loc_id:
        for id in loc_id:
            child_ids += str(id[0])+','
        res = ' and location_id in (%s)' % child_ids[:-1]
    else:
        res = ''
    self.recursive_child_id[location_id] = res
    return res

def recursive_package_child_id(cr, package_id):
    res = self.recursive_package_child_id.get(package_id)
    if res is not None:
        return res

    cr.execute("""
         WITH RECURSIVE child_search(id) AS
          (SELECT id
           FROM stock_quant_package
           WHERE id={id}
           UNION ALL SELECT sl.id
           FROM stock_quant_package sl,
                                    child_search p
           WHERE sl.parent_id=p.id)
        SELECT *
        FROM child_search
    """.format(id = package_id))
    pack_id = cr.fetchall()
    child_ids = ''
    if pack_id:
        for id in pack_id:
            child_ids += str(id[0])+','
        res = ' and package_id in (%s)' % child_ids[:-1]
    else:
        res = ''
    self.recursive_package_child_id[package_id] = res
    return res

def get_history_ids(cr, move_id):
    cr.execute("""
        SELECT quant_id
        FROM stock_quant
        WHERE move_id = %s
    """, move_id)
    return cr.fetchall()

def migrate_packages(cr):
    cr.execute("""
        SELECT value
        FROM ir_config_parameter
        WHERE KEY = 'migration.stock_with_packs.last_stock_move_id'
    """)
    res = cr.fetchone()
    LAST_STOCK_MOVE_ID = None
    if res:
        LAST_STOCK_MOVE_ID = res[0]

    cr.execute("""
        SELECT value
        FROM ir_config_parameter
        WHERE KEY = 'migration.stock_with_packs.last_stock_tracking_id'
    """)
    res = cr.fetchone()
    LAST_STOCK_TRACKING_ID = None
    if res:
        LAST_STOCK_TRACKING_ID = res[0]

    cr.execute("""
        SELECT value
        FROM ir_config_parameter
        WHERE KEY = 'migration.stock_with_packs.type'
    """)
    res = cr.fetchone()
    STOCK_WITH_PACK_TYPE = None
    if res:
        STOCK_WITH_PACK_TYPE = res[0]

    cr.execute("""
INSERT INTO ir_config_parameter (KEY, value)
VALUES ('stock_with_packs',
        'True')
    """)

    if not util.column_exists(cr, 'stock_quant_package', 'old_tracking_id'):
        cr.execute("""
            ALTER TABLE stock_quant_package ADD COLUMN old_tracking_id integer
        """)

    if not LAST_STOCK_TRACKING_ID:
        cr.execute("""
            INSERT INTO stock_quant_package(name, old_tracking_id)
            SELECT concat(name,' - '||serial),
                   id
            FROM stock_tracking;

        """)
    else:
        cr.execute("""
            INSERT INTO stock_quant_package(name, old_tracking_id)
            SELECT concat(name,' - '||serial),
                   id
            FROM stock_tracking
            WHERE id > %s
        """, [int(LAST_STOCK_TRACKING_ID)])

    cr.execute("""
        ANALYZE stock_quant_package
    """)

    if not LAST_STOCK_MOVE_ID:
        cr.execute("""
            SELECT sqp.id "package_id",
                   pick.type "type",
                   move.*
            FROM stock_move MOVE
            LEFT JOIN stock_quant_package sqp ON MOVE.tracking_id = sqp.old_tracking_id
            JOIN stock_picking pick ON MOVE.picking_id = pick.id
            WHERE MOVE.state='done'
            ORDER BY MOVE.picking_id,
                          MOVE.create_date,
                               MOVE.id
        """)
        move_ids = cr.dictfetchall()
    else:
        cr.execute("""
            SELECT sqp.id "package_id", pick.type "type", move.*
            FROM stock_move MOVE
            LEFT JOIN stock_quant_package sqp ON MOVE.tracking_id = sqp.old_tracking_id
            JOIN stock_picking pick ON MOVE.picking_id = pick.id
            WHERE MOVE.state='done'
              AND MOVE.id > %s
            ORDER BY MOVE.picking_id, MOVE.create_date, MOVE.id
        """, [int(LAST_STOCK_MOVE_ID)])
        move_ids = cr.dictfetchall()


    chunk_size = 200
    size = (len(move_ids) + chunk_size - 1) / chunk_size
    qual = 'chunks of %s stock.move records' % chunk_size
    _logger.info("START_MIGRATE_PACKAGES")
    for chunk in util.log_progress(
        util.chunks(move_ids, chunk_size, list),
        qualifier=qual, logger=_logger, size=size):
        preferred_domain = []
        for move in chunk:
            package_id = result_package_id = None

            # we should parametrize this part. The behavior is different from customer to customer
            #if move['type'] == 'out':
            #    result_package_id = move['package_id']
            #elif move['type'] in ('in', 'internal'):
            #    package_id = move['package_id']

            if STOCK_WITH_PACK_TYPE == 'in':
                if move['type'] in ('in', ):
                    result_package_id = move['package_id']
                elif move['type'] in ('out', 'internal', ):
                    package_id = move['package_id']
            elif STOCK_WITH_PACK_TYPE == 'in_out':
                if move['type'] in ('out', 'in'):
                    result_package_id = move['package_id']
                elif move['type'] in ('internal', ):
                    package_id = move['package_id']
            else:
            # else: STOCK_WITH_PACK_TYPE = 'out'
                if move['type'] in ('out',):
                    result_package_id = move['package_id']
                elif move['type'] in ('in', 'internal', ):
                    package_id = move['package_id']

            cr.execute("""
                INSERT INTO stock_pack_operation(
                    picking_id, product_id, product_uom_id, product_qty, date, location_id,
                    location_dest_id, qty_done, lot_id, processed, from_move_id, package_id,
                    result_package_id
                ) VALUES(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) returning id
                """, [move['picking_id'], move['product_id'], move['product_uom'],
                      move['product_qty'], move['date'], move['location_id'],
                      move['location_dest_id'], move['product_qty'], move.get('prodlot_id', None),
                      True, move['id'], package_id, result_package_id])
            op_id = cr.fetchone()[0]

            cr.execute("""
                INSERT INTO stock_move_operation_link (operation_id, move_id, qty)
                VALUES (%s, %s, %s)
            """, [op_id, move['id'], move['product_qty']])

