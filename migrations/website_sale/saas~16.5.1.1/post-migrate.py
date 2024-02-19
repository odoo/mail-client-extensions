# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "website_sale.payment_delivery_methods", util.update_record_from_xml, reset_translations={"arch_db"}
    )
