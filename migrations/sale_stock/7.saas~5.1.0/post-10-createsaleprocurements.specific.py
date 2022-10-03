from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.modules.registry import RegistryManager
import logging
import os
from itertools import groupby
from operator import itemgetter
import datetime

NS = 'openerp.addons.base.maintenance.migrations.sale_stock.saas-5.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    if os.environ.get('ODOO_MIG_S5_SKIP_PROCUREMENTS_CREATION'):
        _migrate(cr, version)

def _migrate(cr, version):
    """For all sale orders that are not delivered yet, create procurements
       to these lines """
    # Check all related moves to sale order lines where the sales order is not
    # done and not shipped and not cancelled
    # Create a procurement group for every sales order related, create a
    # procurement in customers and create a procurement in
    registry = RegistryManager.get(cr.dbname)
    proc_group_obj = registry['procurement.group']
    rule_obj = registry['procurement.rule']
    partner_obj = registry['res.partner']

    where_state = ('cancel', 'draft')
    cr.execute("""
        SELECT sm.sale_line_id,
               sm.id
        FROM stock_move sm,
             sale_order_line sol,
             sale_order so,
             product_product pp,
             product_template pt
        WHERE so.state not in %s
          and pp.product_tmpl_id = pt.id
          and pt.type <> 'service'
          and pp.id = sol.product_id
          and so.id = sol.order_id
          and sm.sale_line_id = sol.id
    """, [where_state])
    sol_dict = {}
    for item in cr.fetchall():
        if not sol_dict.get(item[0]):
            sol_dict[item[0]] = [item[1]]
        else:
            sol_dict[item[0]] += [item[1]]

    cr.execute("""
        SELECT partner_shipping_id
        FROM sale_order
    """)
    shipping_ids = cr.fetchall()
    property_by_partner = dict(
        [(r['id'], r['property_stock_customer'][0])
            for r in partner_obj.read(
                    cr, SUPERUSER_ID,
                    [rec[0]for rec in shipping_ids],
                    ['property_stock_customer'])
                if r.get('property_stock_customer')])

    cr.execute("""
        SELECT id, security_lead
        FROM res_company
    """)
    security_lead_by_company = dict([(r[0], r[1]) for r in cr.fetchall()])

    cr.execute("""
        SELECT procurement_id, state
        FROM stock_move
    """)
    state_by_procurement = dict(
        (k, [v['state'] for v in itr]) for k, itr
        in groupby(
            sorted(cr.dictfetchall(),
                   key=itemgetter('procurement_id')),
            itemgetter('procurement_id')))

    #Search a rule we can assign so it will do the check on the procurement
    rules = rule_obj.search(
        cr, SUPERUSER_ID,
        [('action', '=', 'move'), ('picking_type_id.code', '=', 'outgoing')])
    rule = rules and rules[0] or False

    sql_sale_order_line_read = """\
        SELECT id, name, order_id, product_id, delay, product_uom,
               product_uom_qty, product_uos, product_uos_qty, route_id
        FROM sale_order_line
        WHERE id IN %s
        """
    sql_sale_order_read = """\
        SELECT id, name, procurement_group_id, state, picking_policy,
               order_policy, partner_shipping_id, date_order, company_id,
               warehouse_id
        FROM sale_order
        WHERE id = %s
        """

    chunk_size = 200
    size = (len(sol_dict.keys()) + chunk_size - 1) / chunk_size
    qual = 'chunks of %s sale.order.line records' % chunk_size
    for line_ids in util.log_progress(
        util.chunks(sol_dict.keys(), chunk_size, list),
        qualifier=qual, logger=_logger, size=size):
        cr.execute(
            sql_sale_order_line_read,
            [tuple(line_ids)])
        lines = cr.dictfetchall()
        for line in lines:
            cr.execute(
                sql_sale_order_read,
                [line['order_id']])
            order = cr.dictfetchone()
            order['shipped'] = False

            if not order['procurement_group_id']:
                vals = {
                    'name': order['name'],
                    'partner_id': order['partner_shipping_id'],
                    'move_type': order['picking_policy'],
                }
                group_id = proc_group_obj.create(cr, SUPERUSER_ID, vals)
                cr.execute("""\
                    UPDATE sale_order
                    SET procurement_group_id = %s
                    WHERE id = %s
                """, [group_id, order['id']])
            else:
                group_id = order['procurement_group_id']

            vals = _prepare_order_line_procurement(
                cr, order, line, group_id, property_by_partner,
                security_lead_by_company)

            # Search related moves
            related_moves = sol_dict[line['id']]
            if not isinstance(related_moves, list):
                related_moves = [related_moves]
            proc_state = ('done' if order['shipped']
                          or order['state'] == 'done' else 'running')
            vals.update({
                'move_ids': related_moves,
                'rule_id': rule,
                'state': proc_state})

            proc_id = insert_procurement_order(cr, vals)
            _check(cr, proc_id, state_by_procurement)

            cr.execute("""
                UPDATE procurement_order
                SET group_id = %s
                WHERE id = %s
            """, [group_id, proc_id])
            cr.execute("""
                UPDATE stock_move
                SET group_id = %s
                WHERE id = %s
                """, [group_id, related_moves[0]])
            cr.execute("""\
                SELECT picking_id
                FROM stock_move
                WHERE id = %s
            """, [related_moves[0]])
            picking_id = cr.fetchone()
            cr.execute("""
                UPDATE stock_picking
                SET group_id = %s
                WHERE id = %s
                """, [group_id, picking_id])


def insert_procurement_order(cr, vals):
    cols = ['name', 'origin', 'company_id', 'date_planned',
            'group_id', 'rule_id', 'product_id', 'product_qty', 'product_uom',
            'product_uos_qty', 'product_uos', 'state', 'location_id',
            'partner_dest_id', 'warehouse_id', 'sale_line_id']

    sql = """\
        INSERT INTO procurement_order (
            create_uid, create_date, priority, {0}
        ) values (
            1, now() at time zone 'utc', 1, {1}
        ) RETURNING id""".format(
        ', '.join(cols),
        ', '.join(["%({})s".format(c) for c in cols]))
    cr.execute(sql, vals)
    res = cr.fetchone()
    proc_id = res[0]
    move_ids = vals.pop('move_ids')
    cr.execute("""\
        UPDATE stock_move
        SET procurement_id = %s
        WHERE id IN %s
    """, [proc_id, tuple(move_ids)])
    route_ids = vals.pop('route_ids')
    if route_ids:
        cr.execute("""\
            INSERT INTO stock_location_route_procurement (
                procurement_id, route_id
            ) VALUES (
                %s, %s
            )
        """, [proc_id, route_ids[0]])

    if util.module_installed(cr, 'sale_mrp'):
        for prop_id in vals.pop('property_ids'):
            cr.execute("""
                INSERT INTO procurement_property_rel (
                    procurement_id, property_id
                ) VALUES (
                    %s, %s
                )
            """, [proc_id, prop_id])

    return proc_id

def _check(cr, proc_id, state_by_procurement):
    # purchase mod:
    cr.execute("""
        SELECT purchase_line_id
        FROM procurement_order
        WHERE id = %s
    """, [proc_id])
    if cr.fetchone():
        moves = [rec['state'] for rec in state_by_procurement.get(proc_id, [])]
        if not moves:
            return False
        return all([move['state'] == 'done'for move in moves])

    # mrp mod:
    cr.execute("""\
        SELECT proc.id,
               proc.production_id,
               prod.state
        FROM procurement_order proc,
             mrp_production prod
        WHERE prod.id = proc.production_id
          AND proc.id = %s
        """, [proc_id])
    res = cr.fetchone()
    if res and res['state'] == 'done':
        return True

    moves = [rec['state'] for rec in state_by_procurement.get(proc_id, [])]
    if not moves:
        return True

    cancel_test_list = [move['state'] == 'cancel' for move in moves]
    done_cancel_test_list = [move['state'] in ('done', 'cancel') for move in moves]
    all_done_or_cancel = all(done_cancel_test_list)
    all_cancel = all(cancel_test_list)
    if not all_done_or_cancel:
        return False
    elif all_done_or_cancel and not all_cancel:
        return True
    elif all_cancel:
        cr.execute("""
            INSERT INTO mail_message(
              create_uid, create_date, date,
              model, res_id, message_type, body
            ) VALUES (
              1, now() at time zone 'utc', now() at time zone 'utc',
              'procurement.order', %s, 'comment', %s
            )
        """, [proc_id, 'All stock moves have been cancelled for this procurement.'])
    cr.execute("""\
        UPDATE procurement_order
        SET state = 'cancel'
        WHERE id = %s
    """, [proc_id])
    return False

def _prepare_order_line_procurement(
        cr, order, line, group_id, property_by_partner, security_lead_by_company):
    security_lead = security_lead_by_company[order['company_id']]
    date_planned = datetime.datetime.strptime(
        order['date_order'],
        DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(days=line['delay'] or 0.0)
    date_planned = (date_planned - datetime.timedelta(days=security_lead)).strftime(
        DEFAULT_SERVER_DATETIME_FORMAT)

    property_stock_customer = property_by_partner.get(order['partner_shipping_id'])
    vals = {
        'name': line['name'],
        'origin': order['name'],
        'date_planned': date_planned,
        'product_id': line['product_id'],
        'product_qty': line['product_uom_qty'],
        'product_uom': line['product_uom'],
        'product_uos_qty': (line['product_uos'] and line['product_uos_qty']) \
            or line['product_uom_qty'],
        'product_uos': (line['product_uos'] and line['product_uos']) or line['product_uom'],
        'company_id': order['company_id'],
        'group_id': group_id,
        'invoice_state': (order['order_policy'] == 'picking') and '2binvoiced' or 'none',
        'sale_line_id': line['id'],
        'location_id': property_stock_customer,
        'route_ids': line['route_id'] and [line['route_id']] or [],
        'warehouse_id': order['warehouse_id'] and order['warehouse_id'] or False,
        'partner_dest_id': order['partner_shipping_id'],
    }

    if util.module_installed(cr, 'sale_mrp'):
        cr.execute("""
            SELECT property_id
            FROM sale_order_line_property_rel
            WHERE order_id = %s
        """, [line['id']])
        vals['property_ids'] = [r[0] for r in cr.fetchall()]
    return vals

