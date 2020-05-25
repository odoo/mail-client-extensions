# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    env['stock.warehouse']._check_multiwarehouse_group()
