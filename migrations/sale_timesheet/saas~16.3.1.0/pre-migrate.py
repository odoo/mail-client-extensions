# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "timesheet_ids")
    util.remove_view(cr, "sale_timesheet.view_sale_service_inherit_form2")
