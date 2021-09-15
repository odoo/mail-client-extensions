# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_coupon.mail_template_sale_coupon", util.update_record_from_xml)
