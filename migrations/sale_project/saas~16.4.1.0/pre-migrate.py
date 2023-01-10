# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "project.milestone", "sale_line_name", "sale_line_display_name")
