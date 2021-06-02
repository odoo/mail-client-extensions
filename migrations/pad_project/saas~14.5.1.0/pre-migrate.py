# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pad_project.portal_my_task")
    util.remove_field(cr, "project.project", "pad_availability")
    util.remove_field(cr, "project.task", "pad_availability")
