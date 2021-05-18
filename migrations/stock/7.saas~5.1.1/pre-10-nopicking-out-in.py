from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # Change stock.picking.in/out to stock.picking
    cr.execute(
        "SELECT model, id FROM ir_model WHERE model IN %s", [("stock.picking", "stock.picking.in", "stock.picking.out")]
    )

    ids = dict(cr.fetchall())
    id_sp = ids["stock.picking"]
    id_in = ids["stock.picking.in"]
    id_out = ids["stock.picking.out"]

    # change model of manual fields (if not already present)
    for in_out in [id_in, id_out]:
        cr.execute(
            """UPDATE ir_model_fields in_out
                         SET model_id=%s
                       WHERE model_id=%s
                         AND state='manual'
                         AND NOT EXISTS(
                            SELECT 1
                              FROM ir_model_fields sp
                             WHERE model_id=%s
                               AND name=in_out.name
                         )
                   """,
            [id_sp, in_out, id_sp],
        )

    # remaining manual fields must be reassigned
    cr.execute(
        """SELECT io.id, sp.id
                    FROM ir_model_fields io, ir_model_fields sp
                   WHERE io.model_id IN %s
                     AND sp.model_id = %s
                     AND io.state = 'manual'
                     AND io.name = sp.name
               """,
        [(id_in, id_out), id_sp],
    )
    for o, n in cr.fetchall():
        util.replace_record_references(cr, ("ir.model.fields", o), ("ir.model.fields", n), False)

    cr.execute("DELETE FROM ir_model_fields WHERE model_id IN %s RETURNING id", ((id_in, id_out),))
    fields_ids = tuple(x[0] for x in cr.fetchall())
    if fields_ids:
        cr.execute("DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s", ("ir.model.fields", fields_ids))
    cr.execute("DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s", ("ir.model", (id_in, id_out)))
    util.replace_record_references(cr, ("ir.model", id_in), ("ir.model", id_sp))
    util.replace_record_references(cr, ("ir.model", id_out), ("ir.model", id_sp))
    cr.execute("DELETE FROM ir_model WHERE id IN %s", ((id_in, id_out),))

    # remove duplicated mail_followers
    cr.execute(
        """DELETE FROM mail_followers f
                   WHERE f.res_model = %s
                     AND EXISTS(SELECT 1
                                  FROM mail_followers p
                                 WHERE p.res_model IN %s
                                   AND p.res_id = f.res_id
                                   AND p.partner_id = f.partner_id)
              """,
        ["stock.picking.in", ("stock.picking.out", "stock.picking")],
    )
    cr.execute(
        """DELETE FROM mail_followers f
                   WHERE f.res_model = %s
                     AND EXISTS(SELECT 1
                                  FROM mail_followers p
                                 WHERE p.res_model IN %s
                                   AND p.res_id = f.res_id
                                   AND p.partner_id = f.partner_id)
              """,
        ["stock.picking.out", ("stock.picking.in", "stock.picking")],
    )

    util.rename_model(cr, "stock.picking.out", "stock.picking", rename_table=False)
    util.rename_model(cr, "stock.picking.in", "stock.picking", rename_table=False)

    # Some databases have a size on `state` field. Don't know where this from, but this will
    # forbid to insert new state `partially_available` which is longer than 16 characters.
    cr.execute("ALTER TABLE stock_picking ALTER COLUMN state TYPE character varying")
