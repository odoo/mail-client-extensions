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
        util.make_field_non_stored(cr, "account.return", "state")
