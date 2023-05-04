# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Reserve and confirm moves of Repair Order that were forcefully 'confirmed' in pre-migrate
    cr.execute(
        """
        SELECT m.id
          FROM stock_move m
          JOIN repair_order r
            ON r.id = m.repair_id
         WHERE m.state = 'draft'
           AND r.state = 'confirmed'
           AND m.repair_line_type IS NOT NULL
        """
    )

    move_ids = [id[0] for id in cr.fetchall()]
    if move_ids:
        moves_to_update = util.iter_browse(util.env(cr)["stock.move"], move_ids)
        for move in moves_to_update:
            move._check_company()
            move._adjust_procure_method()
            move._action_confirm()
            move._trigger_scheduler()
