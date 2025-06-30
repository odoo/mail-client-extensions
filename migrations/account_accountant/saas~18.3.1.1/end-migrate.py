from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        SELECT am.company_id,
               array_agg(DISTINCT absl.id) as st_line_ids,
               array_agg(DISTINCT arm.id) as reco_models_ids
          FROM account_bank_statement_line absl
          JOIN account_move am ON absl.move_id = am.id
          JOIN account_reconcile_model arm ON arm.company_id = am.company_id
         WHERE absl.is_reconciled IS NOT TRUE
      GROUP BY am.company_id
    """)

    unreconciled_statement_lines_per_company = {}
    reco_model_per_company = {}
    for company_id, st_line_ids, reco_models_ids in cr.fetchall():
        unreconciled_statement_lines_per_company[company_id] = st_line_ids
        reco_model_per_company[company_id] = reco_models_ids

    env = util.env(cr)
    RecModel = env["account.reconcile.model"]
    StLineModel = env["account.bank.statement.line"]
    for company in env["res.company"].search([]):
        if not reco_model_per_company.get(company.id) or not unreconciled_statement_lines_per_company.get(company.id):
            continue

        for reco_model in util.iter_browse(RecModel, reco_model_per_company[company.id]):
            for st_line in util.iter_browse(
                StLineModel,
                unreconciled_statement_lines_per_company[company.id],
            ):
                reco_model._apply_reconcile_models(st_line)
