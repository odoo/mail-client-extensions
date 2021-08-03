# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "project_overview")
    util.remove_field(cr, "sale.order", "project_overview")
