# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    view_id = util.ref(cr, 'website.layout')
    cr.execute("""UPDATE ir_ui_view
                     SET arch=replace(replace(arch, %s, %s), %s, %s)
                   WHERE id=%s
               """, ('<script type="text/javascript" src="/website/static/lib/bootstrap/js/bootstrap.js"/>',
                     '',
                     ' src="/website/static/src/js/website.snippets.animation.js"/>',
                     ' src="/website/static/src/js/website.snippets.animation.js"></script>\n\
                      <script type="text/javascript" src="/web/static/lib/bootstrap/js/bootstrap.js"></script>',
                     view_id))
