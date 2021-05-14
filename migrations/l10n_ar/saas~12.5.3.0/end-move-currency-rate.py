# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    CURR = env["res.currency"].browse
    COMP = env["res.company"].browse

    cr.execute(
        """
        SELECT m.id, m.currency_id, m.company_id, c.currency_id,
               COALESCE(m.invoice_date, m.write_date::date)
          FROM account_move m
          JOIN res_company c ON c.id = m.company_id
         WHERE m.l10n_ar_currency_rate IS NULL
           AND m.state = 'posted'
    """
    )
    for mid, mcur_id, cid, ccur_id, date in util.log_progress(
        cr.fetchall(), util._logger, qualifier="account.move", size=cr.rowcount
    ):
        rate = CURR(mcur_id)._convert(1.0, CURR(ccur_id), COMP(cid), date, round=False)
        cr.execute("UPDATE account_move SET l10n_ar_currency_rate = %s WHERE id = %s", [rate, mid])
