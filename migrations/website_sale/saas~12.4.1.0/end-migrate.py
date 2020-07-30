# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move m
           SET website_id = i.website_id
          FROM account_invoice i
         WHERE i.move_id = m.id
           AND m.website_id IS NULL
    """
    )
