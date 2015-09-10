# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'ir.attachment', 'datas_big')

    # remove old AbstractModels
    util.delete_model(cr, 'website.qweb', drop_table=False)
    util.delete_model(cr, 'website.qweb.field', drop_table=False)
    for f in "integer float date datetime text selection many2one \
              html image monetary duration relative contact qweb".split():
        util.delete_model(cr, 'website.qweb.field.' + f, drop_table=False)
