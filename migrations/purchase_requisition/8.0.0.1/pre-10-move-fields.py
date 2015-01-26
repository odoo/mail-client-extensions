# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "purchase_requisition", "ordering_date", "date")
    cr.execute("""
        UPDATE purchase_requisition pr
        SET ordering_date = date_start AT TIME ZONE 'UTC' AT TIME ZONE COALESCE(p.tz, 'UTC')
        FROM res_users u, res_partner p
        WHERE COALESCE(pr.user_id, pr.create_uid) = u.id AND
              u.partner_id = p.id;
    """)