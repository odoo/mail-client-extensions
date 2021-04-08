# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "project_project", "pricing_type"):
        cr.execute(
            """
            UPDATE project_project
               SET pricing_type = 'task_rate'
             WHERE is_fsm IS TRUE
            """
        )
