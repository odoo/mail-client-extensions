# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("ALTER TABLE ir_attachment DROP CONSTRAINT IF EXISTS ir_attachment_filename_unique")
    util.remove_field(cr, 'ir.attachment', 'user_id')
    util.remove_field(cr, 'ir.attachment', 'parent_id')
    util.remove_field(cr, 'ir.attachment', 'partner_id')

    models = util.splitlines("""
        directory
        directory.dctx
        directory.content
        directory.content.type
        storage
        configuration
    """)
    for model in models:
        util.delete_model(cr, 'document.' + model)

    util.delete_model(cr, 'report.document.user')
    util.delete_model(cr, 'report.document.file')
