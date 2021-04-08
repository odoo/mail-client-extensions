# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "project_project", "sale_order_id")  # This field will be a related field
