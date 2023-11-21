# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE project_task
           SET progress = progress / 100
        """,
        table="project_task",
    )
