# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.subscription", "uuid", "access_token")
    util.remove_constraint(cr, "sale_subscription", "uuid_uniq")
    util.rename_field(cr, "sale.subscription", "website_url", "access_url")
