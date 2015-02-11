# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model_constraint', 'definition', 'varchar')
    util.delete_model(cr, 'ir.sequence.type')

    if util.column_exists(cr, 'ir_attachment', 'datas_checksum'):
        util.move_field_to_module(cr, 'ir.attachment', 'datas_checksum', 'website', 'base')
        util.rename_field(cr, 'ir.attachment', 'datas_checksum', 'checksum')

    if util.column_exists(cr, 'ir_attachment', 'mimetype'):
        util.move_field_to_module(cr, 'ir.attachment', 'mimetype', 'website', 'base')
