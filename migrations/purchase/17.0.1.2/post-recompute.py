# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "purchase.order.line", ["discount"], strategy="commit")
