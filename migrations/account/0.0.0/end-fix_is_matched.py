from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_between("14.0", "saas~16.3"):
        return

    env = util.env(cr)

    extra_join, extra_where = "", ""
    if util.module_installed(cr, "hr_expense") and util.version_gte("16.0"):
        extra_join = "LEFT JOIN hr_expense_sheet hes ON hes.account_move_id = am.id"
        extra_where = "AND hes.id IS NULL"
    payment_field = "payment_id"
    if util.version_gte("saas~17.5"):
        payment_field = "origin_payment_id"

    query = util.format_query(
        cr,
        """
        SELECT ap.payment_type,
               array_agg(ap.id)
          FROM account_payment ap
          JOIN account_move am ON am.{} = ap.id
          JOIN account_journal aj ON aj.id = am.journal_id
          {}
         WHERE ap.is_matched IS False
           AND aj.type IN ('bank', 'cash')
           AND am.state = 'posted'
           AND ap.is_reconciled IS False
           {}
         GROUP BY ap.payment_type
        """,
        payment_field,
        util.SQLStr(extra_join),
        util.SQLStr(extra_where),
    )
    cr.execute(query)
    for payment_type, payment_ids in cr.fetchall():
        if not payment_ids:
            continue
        util._logger.info("Recomputing is_matched for %s not reconciled %s payments", len(payment_ids), payment_type)
        util.iter_browse(env["account.payment"], payment_ids, strategy="commit")._compute_reconciliation_status()
