# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "sale_crm.sale_action_quotations")
    util.remove_record(cr, "sale_crm.sale_action_orders")
