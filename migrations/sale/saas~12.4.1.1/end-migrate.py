# -*- coding: utf-8 -*-
import psycopg2

from odoo.tools import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move m
           SET team_id = i.team_id,
               partner_shipping_id = i.partner_shipping_id
          FROM account_invoice i
         WHERE i.move_id = m.id
    """
    )
