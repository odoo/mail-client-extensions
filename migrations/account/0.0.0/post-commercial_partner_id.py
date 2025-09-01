# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # because a related field was too complex.
    if not util.column_exists(cr, "account_move", "commercial_partner_id"):
        return
    cr.execute("SELECT id FROM account_move WHERE commercial_partner_id IS NULL AND partner_id IS NOT NULL")
    if cr.rowcount:
        Move = util.env(cr)["account.move"].with_context(mail_notrack=True)
        util.recompute_fields(
            cr, Move, ["commercial_partner_id"], ids=[id_ for (id_,) in cr.fetchall()], strategy="commit"
        )
