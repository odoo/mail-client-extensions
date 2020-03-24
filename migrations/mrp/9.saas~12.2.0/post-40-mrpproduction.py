# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from collections import defaultdict


def migrate(cr, version):
    cr.execute("""update stock_move set is_done=state=ANY(array['done', 'cancel'])""")

    util.recompute_fields(cr, "mrp.production", ("availability",))
    util.recompute_fields(cr, "mrp.workcenter", ("working_state",))
