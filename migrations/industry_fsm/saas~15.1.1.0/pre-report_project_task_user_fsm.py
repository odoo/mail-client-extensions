# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # remove extra columns for databases created before odoo/enterprise#27305 (and forward-ports)
    util.remove_field(cr, "report.project.task.user.fsm", "create_uid")
    util.remove_field(cr, "report.project.task.user.fsm", "write_uid")
    util.remove_field(cr, "report.project.task.user.fsm", "write_date")
