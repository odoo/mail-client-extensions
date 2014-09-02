# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""select noupdate
                   from ir_model_data
                  where name = %s
                    and module = %s
               """, ['footer_custom', 'website'])
    [noupdate] = cr.fetchone() or [False]
    if noupdate:
        footer_default_view_id = util.ref(cr, 'website.footer_default')
        if footer_default_view_id:
            cr.execute("UPDATE ir_ui_view SET active=%s WHERE id=%s",
                       [False, footer_default_view_id])
