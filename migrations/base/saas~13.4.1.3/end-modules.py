# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if not util.has_enterprise():
        util.remove_module(cr, "timer")
