# -*- coding: utf-8 -*-

# performs various checks and displays warnings (or raises exceptions) based on
# the result of these checks

from openerp.addons.base.maintenance.migrations import util

import logging
_logger = logging.getLogger('openerp.addons.base.maintenance.migrations.stock.saas-5.checks')

def migrate(cr, version):
    # Check if an ir.config_parameter exists which would not raise an exception
    # if it does not fulfill the 2 checks below
    # available check overrides: uom2uom
    # if you want to skip errors:
    #   insert into ir_config_parameter (key, value)
    #   values ('migration.skip_rounding_error', 'uom2uom');
    cr.execute("""
        select value from ir_config_parameter where key = 'migration.skip_rounding_error'
        """)
    res = cr.fetchone()

    skip_raise = [rec.strip() for rec in res[0].split(',')] if res else []
    fails = {}

    # 1. check if a given location is not linked to 2 or more wharehouses
    sql_check_location = """
        select wh.{field} as loc_id, loc.name, count(*), array_agg(wh.id) as wh_ids
        from stock_warehouse wh
            inner join stock_location loc
                on wh.{field}=loc.id
        group by wh.{field}, loc.name
        having count(*)  > 1"""

    loc_uniq_msgs = []
    for field in ['lot_input_id', 'lot_output_id', 'lot_stock_id']:
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

    # 2. Automatically fix UoM with rounding = 0
    cr.execute("""
        SELECT
            u.id AS id,
            u.name AS name,
            coalesce(pow(10, -max(
                char_length(split_part(trim(both '0' from product_qty::varchar), '.', 2)))), 1)
                    AS new_rounding
        FROM        product_uom u
        LEFT JOIN   stock_move sm
            ON      sm.product_uom = u.id
        WHERE       u.rounding = 0
        GROUP BY    u.id
        """)
    for uom_id, uom_name, new_rounding in cr.fetchall():
        _logger.warn("Product UoM %s (id %s) has a rounding of 0, setting " \
                     "it up to %s.", uom_name, uom_id, new_rounding)
        cr.execute("""
            UPDATE product_uom SET rounding = %s WHERE id = %s
        """, [new_rounding, uom_id])

    # 3. Check if reconverting the rounding to the default UoM and back to the
    #    original UoM will give errors on stock moves
    cr.execute("""
        select
          m.id as move_id,
          m.product_id as product_id,
          m.product_qty as product_qty,
          m.product_uom as move_uom,
          t.uom_id as default_uom,
          ut.factor as ut_factor,
          um.factor as um_factor,
          ut.rounding as ut_rounding,
          um.rounding as um_rounding,
          um.factor/ut.factor*(
           round(m.product_qty*ut.factor/um.factor,
                 ceil(-log(ut.rounding))::integer )) as computed_qty,
          round(
           um.factor/ut.factor*(round(
               m.product_qty*ut.factor/um.factor,
               ceil(-log(ut.rounding))::integer )),
           ceil(-log(um.rounding))::integer) as rounded_computed_qty
        from
          stock_move m
            inner join product_template t
              on t.id=m.product_id
            inner join product_uom um
              on um.id=m.product_uom
            inner join product_uom ut
              on ut.id=t.uom_id
        where
          t.uom_id != m.product_uom
            and
          m.product_qty != round(
            um.factor/ut.factor*(round(
                m.product_qty*ut.factor/um.factor,
                ceil(-log(ut.rounding))::integer )),
            ceil(-log(um.rounding))::integer)
        order by m.product_id, m.id;""")
    res = cr.dictfetchall()
    if res:
        msgs = []
        for re in res:
            msg = (
                "Move {move_id}: qty: {product_qty} &lt;-&gt; {computed_qty} "
                "default UoM: {default_uom}, move UoM: {move_uom}, "
                "roundings:({ut_rounding}/{um_rounding})"
            ).format(**re)

            msgs.append(msg)
            _logger.warning(msg)

        header = """
        <p>Warning when upgrading Odoo to version {version}.</p>
        <h2>Stock moves that cannot be converted back to their default UoM</h2>

        <p>We have checked that converting a quantity to the default UoM
           and then back to the original UoM will give the same result.<br />
           This is not the case.<br />
           You'll find the list of wrong stock moves further down.
        </p>
        <p>Each line is formated as:<br />
          Move <move id>: qty: <product qty> &lt;-&gt; <computed and
          rounded qty> default UoM: <default uom of the product> UoM:
          <move uom> (<rounding of product UoM>/<rounding of move UoM>)
        </p>"""

        msg = [
            "<ul>",
            '\n  '.join(["<li>%s</li>" % m for m in msgs]),
            "</ul>",
        ]
        header += '\n'.join(msg)
        footer = ""
        util.announce(
            cr, 'saas-5', '', recipient=None, header=header, footer=footer)
        if 'uom2uom' not in skip_raise:
            fails['uom2uom'] = "Quantities on certain stock moves converted " \
                "to the default UoM cannot be reconverted to the same value"

    # 4. Automatically fix UoM used by stock moves that need better precison
    cr.execute("""
        SELECT
            array_agg(sm.id) AS move_ids,
            um.id AS id,
            um.name AS name,
            um.rounding AS rounding,
            pow(10, -max(
                char_length(split_part(trim(both '0' from product_qty::varchar), '.', 2))))
                    AS new_rounding
        FROM        stock_move sm, product_uom um
        WHERE       um.id = sm.product_uom
        AND         state NOT IN ('draft', 'cancel')
        AND         NOT mod(product_qty, um.rounding) = 0
        GROUP BY    um.id
    """)
    if cr.rowcount:
        header = """
        <p>Warning when upgrading Odoo to version {version}.</p>
        <h2>Stock moves should not have more digits specified than the rounding
            of the UoM would expect</h2>

        <p>Some stock moves have been stored using a unit of measure not
           precise enough to store the quantity required. To resolve the issue,
           the rounding of the following units of measure got to be updated:
        </p>

        <ul>
        """
        for move_ids, uom_id, uom_name, rounding, new_rounding \
                in cr.fetchall():
            msg = "Unit of measure %s (id=%s) has now a rounding of %s " \
                  "(was %s) in order to store the quantities of " \
                  "move's ids: %s" % (uom_name, uom_id, new_rounding, rounding,
                                      move_ids)
            _logger.warning(msg)
            header += "<li>%s</li>\n" % msg
            cr.execute("""
                UPDATE product_uom SET rounding = %s WHERE id = %s
            """, [new_rounding, uom_id])
        header += "</ul>\n"
        util.announce(
            cr, 'saas-5', '', recipient=None, header=header, footer='')

    if fails:
        msg = '\n'.join(
            ["check '{}': {}".format(k, v) for k, v in fails.items()])
        _logger.error(msg)
        raise util.MigrationError(msg)
