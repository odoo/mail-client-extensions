# -*- coding: utf-8 -*-

# performs various checks and displays warnings (or raises exceptions) based on
# the result of these checks

from openerp.addons.base.maintenance.migrations import util

import logging
_logger = logging.getLogger('openerp.addons.base.maintenance.migrations.stock.saas-5.checks')

def migrate(cr, version):
    # Check if an ir.config_parameter exists which would not raise an exception
    # if it does not fulfill the 2 checks below
    # available check overrides: uom2uom, move2uom
    # if you want to skip errors:
    #   insert into ir_config_parameter (key, value)
    #   values ('migration.skip_rounding_error', 'uom2uom, move2uom');
    cr.execute("""
        select value from ir_config_parameter where key = 'migration.skip_rounding_error'
        """)
    res = cr.fetchone()

    skip_raise = [rec.strip() for rec in res[0].split(',')] if res else []
    fails = {}

    # check if a given location is not linked to 2 or more wharehouses:
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

    # check if some product uom have a rounding of 0:
    cr.execute("""
        select
            u.id as u_id,
            u.name as uom_name,
            c.name as cat_name,
            u.uom_type
        from product_uom u
            inner join product_uom_categ c
                on c.id=u.category_id
        where u.rounding = 0
        order by u.id""")

    res = cr.fetchall()
    if res:
        msgs = [
            "Some product UoM have a rounding=0",
            "We cannot perform an update. List of UoM:",
            '\n'.join([u'''Uom {re[0]}: name="{re[1]}", category="{re[2]}", type="{re[3]}"'''.format(re=re)
                       for re in res]),
        ]
        # no skip here because the update will fail anyway:
        msg = '\n'.join(msgs)
        _logger.error(msg)
        raise util.MigrationError(msg)

    # Check if reconverting the rounding to the default UoM and back to the
    # original UoM will give errors on stock moves
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
                 round(-log(ut.rounding))::integer )) as computed_qty,
          round(
           um.factor/ut.factor*(round(
               m.product_qty*ut.factor/um.factor,
               round(-log(ut.rounding))::integer )),
           round(-log(um.rounding))::integer) as rounded_computed_qty
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
                round(-log(ut.rounding))::integer )),
            round(-log(um.rounding))::integer)
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

    # Check if there are stock moves with UoMs that have more digits than would
    # be expected of the UoM's rounding
    cr.execute("""
        select
          sm.id,
          sm.product_qty,
          trunc(product_qty, round(-log(um.rounding))::integer)
            as truncated_product_qty,
          um.rounding
        from stock_move sm, product_uom um
        where um.id = sm.product_uom
          and state not in ('draft', 'cancel')
          and trunc(product_qty, round(-log(um.rounding))::integer) - product_qty != 0
        order by sm.id
    """)

    res = cr.fetchall()
    if res:
        msgs = []
        for re in res:
            msg = "Move {re[0]}: actual qty: {re[1]}, expected qty: " \
                "{re[2]} using 'rounding'={re[3]}".format(re=re)
            _logger.warning(msg)
            msgs.append(msg)
        header = """
        <p>Warning when upgrading Odoo to version {version}.</p>
        <h2>Stock moves should not have more digits specified than the rounding
            of the UoM would expect</h2>

        <p>We have checked that the stock move quantities do not have more
           digits than the rounding of the UoM would expect.<br />
           This is not the case.<br />
           Here is the list of wrong stock moves:
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

        if 'move2uom' not in skip_raise:
            fails['move2uom'] = "Quantities on certain stock moves should " \
                "not have more digits specified than the rounding of the " \
                "UoM would expect"

    if fails:
        msg = '\n'.join(
            ["check '{}': {}".format(k, v) for k, v in fails.items()])
        _logger.error(msg)
        raise util.MigrationError(msg)
