# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web.benchmark_suite")
    util.remove_view(cr, "web.assets_backend_legacy_lazy")
