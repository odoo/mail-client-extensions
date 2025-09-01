# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        SELECT array_agg(id ORDER BY id DESC)
        FROM ir_model_fields
        GROUP BY model_id, name
        HAVING count(*) > 1
    """)
    dupes = {x: f[0][0] for f in cr.fetchall() for x in f[0][1:]}
    if dupes:
        util.replace_record_references_batch(cr, dupes, "ir.model.fields")
        for d in dupes:
            util.remove_record(cr, ("ir.model.fields", d))

    cr.execute("""
        UPDATE ir_model_fields f
        SET model = m.model
        FROM ir_model m
        WHERE m.id = f.model_id
    """)
