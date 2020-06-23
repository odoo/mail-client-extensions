# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_ebay.ir_cron_sale_ebay_status_5")
    util.remove_record(cr, "sale_ebay.ir_cron_sale_ebay_status_10")

    util.update_record_from_xml(cr, "sale_ebay.ir_cron_sale_ebay_orders_sync")
    util.update_record_from_xml(cr, "sale_ebay.ir_cron_sale_ebay_stock_sync")
