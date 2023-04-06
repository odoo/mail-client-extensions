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

    util.create_column(cr, 'ir_ui_view', 'key', 'varchar')
    cr.execute("""
        UPDATE ir_ui_view v
           SET key=CONCAT(imd.module, '.', imd.name)
          FROM ir_model_data imd
         WHERE imd.model = 'ir.ui.view'
           AND imd.res_id = v.id
           AND v."type" = 'qweb'
    """)

    util.rename_field(cr, 'res.partner', 'ean13', 'barcode')
