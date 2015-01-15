import logging

from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.stock.saas-5.'
_logger = logging.getLogger(NS + __name__)

def sanitize_warehouses(cr):
    cr.execute("""
        SELECT  array_agg(wh.id) AS warehouses
        ,       array_agg(wh.partner_id) AS partners
        ,       array_agg(wh.lot_input_id) AS lot_inputs
        ,       min(wh.id) AS main_wh
        FROM    stock_warehouse wh
        GROUP BY wh.company_id, wh.lot_output_id, wh.lot_stock_id
        HAVING count(wh.id) > 1
        """)
    for warehouses, partners, lot_inputs, main_wh in cr.fetchall():
        if len(set(filter(None, partners))) > 1:
            raise util.MigrationError(
                "Warehouses %s have the same output and stock locations. "
                "This could be fixed if they were all using the same "
                "partner. Can not continue."
                % (", ".join(map(str, warehouses))))
        warehouses_to_delete = list(set(warehouses) - set([main_wh]))
        cr.execute("""
            SELECT id FROM stock_warehouse_orderpoint
                WHERE warehouse_id = ANY(%s)
            """, [warehouses_to_delete])
        if cr.rowcount:
            raise util.MigrationError(
                "There are order points linked to the warehouses I'm willing "
                "to delete. This is probably wrong. Order points: %s"
                % ", ".join(str(x) for x, in cr.fetchall()))
        if util.table_exists(cr, 'sale_order') and \
           util.column_exists(cr, 'sale_order', 'warehouse_id'):
            cr.execute("""
                SELECT id FROM sale_order WHERE warehouse_id = ANY(%s)
                """, [warehouses_to_delete])
            if cr.rowcount:
                raise util.MigrationError(
                    "There are sale orders linked to the warehouses I'm willing "
                    "to delete. This is probably wrong. Sale orders: %s"
                    % ", ".join(str(x) for x, in cr.fetchall()))
        if util.table_exists(cr, 'sale_shop'):
            cr.execute("""
                SELECT id FROM sale_shop WHERE warehouse_id = ANY(%s)
                """, [warehouses_to_delete])
            if cr.rowcount:
                raise util.MigrationError(
                    "There are sale's shops linked to the warehouses I'm "
                    "willing to delete. This is probably wrong. "
                    "Sale shop: %s"
                    % ", ".join(str(x) for x, in cr.fetchall()))
        if util.table_exists(cr, 'purchase_order'):
            cr.execute("""
                ALTER TABLE purchase_order ADD COLUMN lot_input_id integer;
                UPDATE  purchase_order
                SET     lot_input_id = wh.lot_input_id
                FROM    purchase_order purchase
                JOIN    stock_warehouse wh
                ON      wh.id = purchase.warehouse_id
                WHERE   purchase.id = purchase_order.id
                AND     purchase.warehouse_id = ANY(%s);
                """, [warehouses_to_delete])
        cr.execute("""
            UPDATE  purchase_order
            SET     warehouse_id = %s
            WHERE   warehouse_id = ANY(%s)
            RETURNING id
            """, [main_wh, warehouses_to_delete])
        _logger.warn("[%s purchase order's warehouse set to %s] "
                     "because their warehouse is going to be deleted: %s",
                     cr.rowcount, main_wh,
                     ", ".join(str(x) for x, in cr.fetchall()))
        # NOTE: just in case the main warehouse doesn't have a partner_id, pick
        #       the unique one from the warehouses that going to be deleted
        cr.execute("""
            UPDATE stock_warehouse SET partner_id = %s WHERE id = %s
            """, [sorted(partners).pop(), main_wh])
        cr.execute("""
            DELETE FROM stock_warehouse WHERE id = ANY(%s) RETURNING id
            """, [warehouses_to_delete])
        _logger.warn("[%s warehouses deleted, id=%s kept] "
                     "There must be only one warehouse per input location: %s",
                     cr.rowcount, main_wh,
                     ", ".join(str(x) for x, in cr.fetchall()))

def check_warehouses(cr):
    sql_check_location = """
        select wh.{field} as loc_id, loc.name, count(*), array_agg(wh.id) as wh_ids
        from stock_warehouse wh
            inner join stock_location loc
                on wh.{field}=loc.id
        group by wh.{field}, loc.name, wh.company_id
        having count(*)  > 1"""

    loc_uniq_msgs = []
    for field in ['lot_input_id', 'lot_stock_id']:
        cr.execute(sql_check_location.format(field=field))
        checks = cr.dictfetchall()
        for check in checks:
            loc_uniq_msgs.append(
                ("Stock location '{name}' (id={loc_id}) is linked to more than " \
                "one warehouse (ids={wh_ids}). This is not allowed in Odoo version 8.0.\n" \
                "table: 'stock_warehouse', field: '{field}'").format(field=field, **check))

    if loc_uniq_msgs:
        msg = '\n'.join(loc_uniq_msgs)
        _logger.error(msg)
        raise util.MigrationError(msg)

def migrate(cr, version):
    sanitize_warehouses(cr)
    check_warehouses(cr)
