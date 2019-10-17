# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.env(cr)["res.company"].create_missing_unbuild_sequences()
