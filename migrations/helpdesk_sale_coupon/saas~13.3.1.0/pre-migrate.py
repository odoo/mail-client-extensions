# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "helpdesk_sale_coupon.access_helpdesk_sale_coupon_generate_sale")
