from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_between("14.0", "saas~16.3"):
        return

    env = util.env(cr)

    extra_join, extra_where = "", ""
    if util.module_installed(cr, "hr_expense") and util.version_gte("16.0"):
        extra_join = "LEFT JOIN hr_expense_sheet hes ON hes.account_move_id = am.id"
        extra_where = "AND hes.id IS NULL"

    cr.execute(
        """
               SELECT array_agg(ap.id)
                 FROM account_payment ap
                 JOIN account_move am ON am.payment_id = ap.id
                 JOIN account_journal aj ON aj.id = am.journal_id
                 {}
                WHERE ap.is_matched IS FALSE
                  AND aj.type IN ('bank', 'cash')
                  {}
               """.format(
            extra_join, extra_where
        )
    )
    payment_ids = cr.fetchone()[0] or []
    util.iter_browse(env["account.payment"], payment_ids)._compute_reconciliation_status()
