# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.payment.method", "adyen_latest_diagnosis")
