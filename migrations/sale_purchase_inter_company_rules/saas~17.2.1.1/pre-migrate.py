# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.company", "copy_lots_delivery", "sync_delivery_receipt")
    util.rename_field(cr, "res.config.settings", "copy_lots_delivery", "sync_delivery_receipt")
