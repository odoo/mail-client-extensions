# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_sale.mail_template_sale_cart_recovery", util.update_record_from_xml)
