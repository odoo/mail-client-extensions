# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from collections import defaultdict


def migrate(cr, version):
    cr.execute("""update stock_move set is_done=state=ANY(array['done', 'cancel'])""")

    to_recompute = [
        ['mrp.production', ('availability',)],
        ['mrp.workcenter', ('working_state',)],
    ]
    for model, fields in to_recompute:
        cr.execute("""SELECT id FROM %s""" % util.table_of_model(cr, model))
        ids = [row[0] for row in cr.fetchall()]
        util.recompute_fields(
            cr, model,
            fields=fields,
            ids=ids,
        )
