# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_amazon.ir_cron_sync_amazon_cancellations")
    util.remove_record(cr, "sale_amazon.ir_cron_sync_amazon_cancellations_ir_actions_server")

    util.remove_field(cr, "sale.order", "amazon_cancellation_pending")
