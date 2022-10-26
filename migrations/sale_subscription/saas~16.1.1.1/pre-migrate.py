# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS sale_subscription_report CASCADE")
    util.change_field_selection_values(cr, "sale.order.alert", "action", {"email": "mail_post"})
