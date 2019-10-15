# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "worksheet_signed_by", "varchar")
    util.create_column(cr, "project_worksheet_template", "color", "int4")

    cr.execute("UPDATE project_worksheet_template SET color=0")
