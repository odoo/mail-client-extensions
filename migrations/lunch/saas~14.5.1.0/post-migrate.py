# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "lunch.lunch_order_mail_supplier", util.update_record_from_xml)
