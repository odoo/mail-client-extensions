# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "product.template", "hs_code", "delivery", "delivery_hs_code")
    util.remove_view(cr, "delivery.product_template_hs_code")  # not the same in new module

    util.remove_record_if_unchanged(cr, "delivery.mail_template_data_delivery_confirmation")
