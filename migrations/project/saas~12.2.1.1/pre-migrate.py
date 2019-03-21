# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "date_start")
    util.remove_field(cr, "report.project.task.user", "date_start")
