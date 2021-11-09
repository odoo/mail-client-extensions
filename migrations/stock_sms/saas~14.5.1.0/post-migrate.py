# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "stock_sms.sms_template_data_stock_delivery", util.update_record_from_xml, reset_translations={"body"}
    )
