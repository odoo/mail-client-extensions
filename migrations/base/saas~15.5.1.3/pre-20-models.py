# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "ir.module.module.dependency", "write_date")
    util.remove_field(cr, "ir.module.module.dependency", "create_date")
    util.remove_field(cr, "ir.module.module.dependency", "write_uid")
    util.remove_field(cr, "ir.module.module.dependency", "create_uid")
