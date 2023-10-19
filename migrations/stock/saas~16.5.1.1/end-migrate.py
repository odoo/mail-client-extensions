# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """ SELECT id
                   FROM stock_move
                   WHERE picked = 'f'
                   AND state != 'done'
               """
    )
    move_ids = cr.fetchall()
    if move_ids:
        move_ids = [x[0] for x in move_ids]
        util.env(cr)["stock.move"].browse(move_ids)._do_unreserve()
        util.env(cr)["stock.move"].browse(move_ids)._set_quantity()
