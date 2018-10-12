# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "product.template", "hs_code")
    util.remove_view(cr, "delivery.product_template_hs_code")

    util.remove_record_if_unchanged(cr, "delivery.mail_template_data_delivery_confirmation")
