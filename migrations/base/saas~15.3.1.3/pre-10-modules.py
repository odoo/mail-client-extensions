# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(cr)
