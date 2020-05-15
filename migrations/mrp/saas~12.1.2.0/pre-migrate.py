# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'mrp.production', 'availability', 'reservation_state')
    util.remove_field(cr, 'mrp.production', 'check_to_done')
    util.remove_field(cr, 'mrp.production', 'has_moves')
    util.remove_field(cr, "mrp.workorder", "is_first_wo")
    util.remove_field(cr, "mrp.bom.line", "has_attachments")
