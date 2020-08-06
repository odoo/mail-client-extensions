# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM hr_leave
         WHERE duration_display IS NULL
    """
    )
    leave_ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "hr.leave", ["duration_display"], ids=leave_ids)
