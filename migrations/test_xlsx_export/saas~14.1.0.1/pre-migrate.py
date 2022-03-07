# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # onwards saas~14.1 'export.computed.binary' model is depricated.
    util.remove_model(cr, "export.computed.binary")
