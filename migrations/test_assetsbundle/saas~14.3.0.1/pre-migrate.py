# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "test_assetsbundle.bundle2")
    util.remove_view(cr, "test_assetsbundle.bundle3")
