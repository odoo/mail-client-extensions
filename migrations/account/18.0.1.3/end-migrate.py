from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    for company in env["res.company"].search([("chart_template", "!=", False)], order="parent_path"):
        ChartTemplate = env["account.chart.template"].with_company(company)
        ChartTemplate._load_data(
            {
                "account.reconcile.model": {
                    # Load only the newly introduced reconcile models in 18.0
                    k: v
                    for k, v in ChartTemplate._get_account_reconcile_model(company.chart_template).items()
                    if k in {"reconcile_bill", "internal_transfer_reco"}
                }
            },
            ignore_duplicates=True,
        )

    cr.execute(
        """
        UPDATE account_reconcile_model_line arml
           SET account_id = rc.transfer_account_id
          FROM account_reconcile_model arm
          JOIN res_company rc
            ON arm.company_id = rc.id
          JOIN ir_model_data imd
            ON imd.res_id = arm.id
           AND imd.model = 'account.reconcile.model'
         WHERE imd.name = rc.id || '_internal_transfer_reco'
           AND arm.id = arml.model_id
           AND arml.account_id IS NULL
           AND rc.transfer_account_id IS NOT NULL
        """
    )
