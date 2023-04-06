# -*- coding: utf-8 -*-
from odoo.upgrade import util


def _get_repartition_lines(
    invoice_base_tag, refund_base_tag, invoice_tax_tag=None, refund_tax_tag=None, tax_account=None
):
    return {
        "invoice_repartition_line_ids": [
            (0, 0, {"factor_percent": 100, "repartition_type": "base", "tag_ids": [invoice_base_tag.id]}),
            (
                0,
                0,
                {
                    "factor_percent": 100,
                    "repartition_type": "tax",
                    "account_id": tax_account,
                    "tag_ids": invoice_tax_tag and [invoice_tax_tag.id] or [],
                },
            ),
        ],
        "refund_repartition_line_ids": [
            (0, 0, {"factor_percent": 100, "repartition_type": "base", "tag_ids": [refund_base_tag.id]}),
            (
                0,
                0,
                {
                    "factor_percent": 100,
                    "repartition_type": "tax",
                    "account_id": tax_account,
                    "tag_ids": refund_tax_tag and [refund_tax_tag.id] or [],
                },
            ),
        ],
    }


def migrate(cr, version):
    env = util.env(cr)
    product_query = """
        SELECT pt.id, item_code.code, item_code.description, item_code.id, item_code.tax_rate
          FROM product_template pt
          JOIN product_product pp
            ON pp.product_tmpl_id = pt.id
          JOIN account_move_line aml
            ON pp.id = aml.product_id
          JOIN l10n_ke_item_code item_code
            ON pt.l10n_ke_hsn_code = item_code.code
      GROUP BY pt.id, item_code.code, item_code.description, item_code.id, item_code.tax_rate
    """
    cr.execute(product_query)
    codes = cr.fetchall()

    # Expressions, used to retrieve account tags
    expression_eight_base = env.ref("l10n_ke.tax_report_other_rate_sales_base_tag")
    expression_eight_tax = env.ref("l10n_ke.tax_report_other_rate_sales_tax_tag")
    expression_zero_base = env.ref("l10n_ke.tax_report_zero_rated_sales_base_tag")
    expression_exempt_base = env.ref("l10n_ke.tax_report_exempt_sales_base_tag")

    # Tax tags, used on repartition lines
    ke_country_id = env.ref("base.ke").id
    tags_eight_base_invoice, tags_eight_base_refund = (
        env["account.account.tag"]._get_tax_tags(expression_eight_base.formula, ke_country_id).sorted("tax_negate")
    )
    tags_eight_tax_invoice, tags_eight_tax_refund = (
        env["account.account.tag"]._get_tax_tags(expression_eight_tax.formula, ke_country_id).sorted("tax_negate")
    )
    tags_zero_base_invoice, tags_zero_base_refund = (
        env["account.account.tag"]._get_tax_tags(expression_zero_base.formula, ke_country_id).sorted("tax_negate")
    )
    tags_exempt_base_invoice, tags_exempt_base_refund = (
        env["account.account.tag"]._get_tax_tags(expression_exempt_base.formula, ke_country_id).sorted("tax_negate")
    )

    company_ids = env["res.company"].search([("chart_template", "=", "ke")])
    for company in company_ids:
        rep_account_id = util.ref(cr, f"account.{company.id}_ke2200")
        tax_group_zero_id = util.ref(cr, f"account.{company.id}_tax_group_0")
        tax_group_eight_id = util.ref(cr, f"account.{company.id}_tax_group_8")

        tax_rate_dict = {
            "B": {
                "amount": 8,
                "invoice_label": "Sales VAT (8%)",
                "tax_group_id": tax_group_eight_id,
                **_get_repartition_lines(
                    tags_eight_base_invoice,
                    tags_eight_base_refund,
                    tags_eight_tax_invoice,
                    tags_eight_tax_refund,
                    rep_account_id,
                ),
            },
            "C": {
                "amount": 0,
                "invoice_label": "Sales VAT Zero",
                "tax_group_id": tax_group_zero_id,
                **_get_repartition_lines(tags_zero_base_invoice, tags_zero_base_refund),
            },
            "E": {
                "amount": 0,
                "invoice_label": "Sales VAT Exempt",
                "tax_group_id": tax_group_zero_id,
                **_get_repartition_lines(tags_exempt_base_invoice, tags_exempt_base_refund),
            },
        }
        # Create a new tax for each item code
        for product_template_id, code, description, item_code_id, tax_rate in codes:
            new_tax = (
                env["account.tax"]
                .with_company(company)
                .create(
                    {
                        "name": ("8% " if tax_rate == "B" else "0% " if tax_rate == "C" else "Exempt ") + code,
                        "description": description,
                        "l10n_ke_item_code_id": item_code_id,
                        **tax_rate_dict[tax_rate],
                    }
                )
            )
            env["product.template"].browse(product_template_id).taxes_id += new_tax

    util.remove_field(cr, "product.product", "l10n_ke_hsn_code")
    util.remove_field(cr, "product.product", "l10n_ke_hsn_name")

    util.remove_field(cr, "product.template", "l10n_ke_hsn_code")
    util.remove_field(cr, "product.template", "l10n_ke_hsn_name")
