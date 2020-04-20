# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.fixup_m2m(cr, "res_groups_implied_rel", "res_groups", "res_groups", "gid", "hid")
