# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "sale_amazon.order_sync_failure", util.update_record_from_xml, reset_translations={"subject", "body_html"}
    )
