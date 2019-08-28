# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # reassign PO with an origin as created by the system (OdooBot)
    cr.execute("""
        UPDATE purchase_order
           SET create_uid = 1, user_id = 1
         WHERE origin IS NOT NULL
           AND create_uid = %s
    """, [util.ENVIRON["user2_id"]])
