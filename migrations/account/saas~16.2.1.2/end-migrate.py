from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    cr.execute("DELETE FROM ir_config_parameter WHERE key='account.show_line_subtotals_tax_selection'")

    # Update allow_out_payment. Set it to false unless there is an outgoing payment with a payment method that requires a bank
    # account and that is already reconciled.
    payment_method_requiring_bank_account = env["account.payment"]._get_method_codes_needing_bank_account()
    if payment_method_requiring_bank_account:
        cr.execute(
            """
            WITH banks AS (
                SELECT bank.id,
                       bool_or(p.has is true) AS allow_out_payment
                  FROM res_partner_bank bank
             LEFT JOIN LATERAL (
                    SELECT true as has
                      FROM account_payment payment
                      JOIN account_payment_method_line apml
                        ON payment.payment_method_line_id = apml.id
                      JOIN account_payment_method apm
                        ON apml.payment_method_id = apm.id
                     WHERE payment.partner_bank_id = bank.id
                       AND payment.payment_type = 'outbound'
                       AND payment.is_reconciled
                       AND apm.code IN %s
                ) AS p ON (true)
                GROUP BY bank.id
            )
            UPDATE res_partner_bank b
               SET allow_out_payment = banks.allow_out_payment
              FROM banks
             WHERE banks.id = b.id
               AND b.allow_out_payment IS DISTINCT FROM banks.allow_out_payment
        """,
            (tuple(payment_method_requiring_bank_account),),
        )

    util.recompute_fields(cr, "res.partner.bank", ["has_iban_warning", "has_money_transfer_warning"])

    # Reload existing journals and accounts to create xmlids if they do not have them
    for company in env["res.company"].search([("chart_template", "!=", False)]):
        ChartTemplate = env["account.chart.template"].with_company(company)
        if not ChartTemplate._get_chart_template_mapping().get(company.chart_template):
            continue  # custom CoA
        data = ChartTemplate._get_chart_template_data(company.chart_template)
        template_data = data.pop("template_data")
        data = {model: data[model] for model in ("account.journal", "account.account") if model in data}
        ChartTemplate._pre_reload_data(company, template_data, data)
