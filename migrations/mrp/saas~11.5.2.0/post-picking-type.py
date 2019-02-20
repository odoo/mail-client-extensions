# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.import_script("stock/saas~11.5.1.1/post-picking-type.py").migrate(cr, version)
