#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_ui_view', 'customize_show', 'boolean')

    cr.execute("""UPDATE ir_ui_view
                     SET customize_show = (application != %s)
               """, ['always'])
