# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "sale_order_ids")  # computed m2m
