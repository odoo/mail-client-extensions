# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # rename field. column will be deleted in post- script
    util.rename_field(cr, "sale.order", "ups_carrier_account", "partner_ups_carrier_account")
    util.remove_field(cr, "sale.order", "ups_service_type")

    util.remove_field(cr, "stock.picking", "ups_carrier_account")
    util.remove_field(cr, "stock.picking", "ups_service_type")

    util.remove_view(cr, "delivery_ups.view_picking_withcarrier_out_form_inherit_delivery_ups")
