# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for suffix in {"enabled", "username", "password", "access_token", "access_token_validity"}:
        util.remove_field(cr, "payment.acquirer", "paypal_api_{}".format(suffix))
