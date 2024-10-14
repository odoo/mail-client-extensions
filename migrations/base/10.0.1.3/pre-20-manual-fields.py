# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(r"""
        SELECT id, model, related
          FROM ir_model_fields
         WHERE name LIKE 'x\_%'
           AND state = 'base'
           AND related IS NOT NULL
    """)

    toup = []

    for fid, model, related in cr.fetchall():
        path = related.split(".")
        comodel = model
        for field in path:
            cr.execute("SELECT relation, state FROM ir_model_fields WHERE model=%s AND name=%s", [comodel, field])
            if not cr.rowcount:
                # badly defined related, ignore
                break
            comodel, state = cr.fetchone()
            if state == "manual":
                toup.append(fid)
                break
            if not comodel:
                # badly defined related, ignore
                break

    cr.execute("UPDATE ir_model_fields SET state='manual' WHERE id=ANY(%s)", [toup])

    cr.execute("UPDATE ir_model_fields SET selection='[]' WHERE selection IS NULL AND ttype='selection'")
