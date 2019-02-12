# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "ir.server.object.lines", "type", "evaluation_type")

    util.remove_field(cr, "ir.attachment", "res_model_name")
    if not util.module_installed(cr, "documents"):
        util.remove_field(cr, "ir.attachment", "active")
        util.remove_field(cr, "ir.attachment", "thumbnail")
    else:
        util.move_field_to_module(cr, "ir.attachment", "active", 'base', 'documents')
        util.move_field_to_module(cr, "ir.attachment", "thumbnail", 'base', 'documents')
