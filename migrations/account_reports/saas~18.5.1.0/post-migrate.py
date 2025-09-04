from odoo.upgrade import util


def migrate(cr, version):
    if util.parse_version(version) >= util.parse_version("saas~18.3"):
        cr.execute("""
        UPDATE account_return
           SET generic_state_review_submit = CASE
                    WHEN (ir_model_data.module || '.' || ir_model_data.name) IN (
                        'account_reports.annual_corporate_tax_return_type',
                        'l10n_be_intrastat.be_intrastat_goods_return_type',
                        'l10n_be_reports.be_vat_listing_return_type',
                        'l10n_be_reports.be_ec_sales_list_return_type'
                    )
                    THEN COALESCE(state, 'new')
                END,
                generic_state_only_pay = CASE
                    WHEN (ir_model_data.module || '.' || ir_model_data.name) = 'l10n_be_reports.be_isoc_prepayment_return_type'
                    THEN COALESCE(state, 'new')
                END,
                generic_state_tax_report = CASE
                    WHEN (ir_model_data.module || '.' || ir_model_data.name) NOT IN (
                        'account_reports.annual_corporate_tax_return_type',
                        'l10n_be_intrastat.be_intrastat_goods_return_type',
                        'l10n_be_reports.be_vat_listing_return_type',
                        'l10n_be_reports.be_ec_sales_list_return_type',
                        'l10n_be_reports.be_isoc_prepayment_return_type'
                    )
                    THEN COALESCE(state, 'new')
                END
          FROM ir_model_data
         WHERE account_return.type_id = ir_model_data.res_id
           AND ir_model_data.model = 'account.return.type';
        """)

    cr.execute(
        """
        UPDATE account_return_type t
           SET states_workflow = (
                CASE WHEN t.category = 'audit' THEN 'generic_state_review'
                     WHEN %(tax_report_id)s IN (t.report_id, r.root_report_id) THEN 'generic_state_tax_report'
                     WHEN %(ec_sales_list_report_id)s IN (t.report_id, r.root_report_id) THEN 'generic_state_review_submit'
                     ELSE 'generic_state_review'
                END)
          FROM account_report r
         WHERE t.states_workflow IS NULL
           AND r.id = t.report_id
    """,
        {
            "tax_report_id": util.ref(cr, "account.generic_tax_report"),
            "ec_sales_list_report_id": util.ref(cr, "account_reports.generic_ec_sales_report"),
        },
    )

    cr.execute("""
        UPDATE account_return_type t
           SET states_workflow = 'generic_state_review'
         WHERE t.states_workflow IS NULL
           AND t.report_id IS NULL
    """)
