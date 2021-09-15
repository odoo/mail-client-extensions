# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mass_mailing_sale.mass_mail_sale_order_0", util.update_record_from_xml)
