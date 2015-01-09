# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    vid = util.ref(cr, 'payment_ogone.ogone_acquirer_button')
    if vid:
        cr.execute("""UPDATE ir_ui_view
                         SET arch=replace(arch, 'type="image" name="submit"', 'type="submit"')
                       WHERE id=%s
                   """, [vid])
