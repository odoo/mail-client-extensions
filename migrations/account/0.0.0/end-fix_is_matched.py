from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_between("14.0", "saas~16.3"):
        return

    env = util.env(cr)
    cr.execute(
        """
               SELECT array_agg(ap.id)
                 FROM account_payment ap
                 JOIN account_move am ON am.payment_id = ap.id
                 JOIN account_journal aj ON aj.id = am.journal_id
                WHERE ap.is_matched IS FALSE
                  AND aj.type IN ('bank', 'cash')
               """
    )
    payment_ids = cr.fetchone()[0] or []
    util.iter_browse(env["account.payment"], payment_ids)._compute_reconciliation_status()
