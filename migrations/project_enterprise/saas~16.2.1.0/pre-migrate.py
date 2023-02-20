# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "allocated_hours")
    util.remove_field(cr, "project.task", "allocation_type")
    util.remove_field(cr, "project.task", "duration")
    util.remove_field(cr, "report.project.task.user", "allocated_hours")
