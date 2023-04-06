# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_field_usage(cr, "sale.order", "categ_ids", "tag_ids")
