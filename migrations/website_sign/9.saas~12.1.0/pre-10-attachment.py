# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    imp = util.import_script('base/9.0.1.3/post-20-binary_field_as_attachment.py')
    imp.convert(cr, 'signature.request', 'completed_document')
    imp.convert(cr, 'signature.request.item', 'signature')
