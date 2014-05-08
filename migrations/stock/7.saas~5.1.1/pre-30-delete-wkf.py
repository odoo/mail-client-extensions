# -*- coding: utf-8 -*-
def migrate(cr, version):
    """Delete procurement order wkf """

    cr.execute("""DELETE FROM wkf WHERE osv=%s
               """, ('stock.picking',))
