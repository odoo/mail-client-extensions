import itertools


def migrate(cr, version):
    tax_names = [
        "vat_sale_26",
        "vat_sale_26_incl",
        "vat_purchase_26",
        "vat_purchase_26_incl",
        "vat_purchase_26_invest",
        "vat_purchase_26_invest_incl",
        "vat_sale_38",
        "vat_sale_38_incl",
        "vat_purchase_38",
        "vat_purchase_38_incl",
        "vat_purchase_38_invest",
        "vat_purchase_38_invest_incl",
        "vat_sale_81",
        "vat_sale_81_incl",
        "vat_purchase_81",
        "vat_purchase_81_incl",
        "vat_purchase_81_invest",
        "vat_purchase_81_invest_incl",
        "vat_purchase_81_return",
        "vat_purchase_81_reverse",
    ]
    cr.execute("SELECT id FROM res_company WHERE chart_template = 'ch'")
    if cr.rowcount:
        companies = [row[0] for row in cr.fetchall()]
        xmlids = tuple(f"{c_id}_{name}" for c_id, name in itertools.product(companies, tax_names))
        cr.execute(
            """
            WITH tax_ids AS (
                 SELECT res_id
                   FROM ir_model_data
                  WHERE module = 'account'
                    AND name IN %s
               )
            UPDATE account_tax_repartition_line l
               SET sequence = CASE WHEN l.repartition_type = 'base' THEN 1
                              ELSE 2
                              END
              FROM tax_ids
             WHERE l.tax_id = tax_ids.res_id
               AND l.sequence IS NULL
            """,
            [
                xmlids,
            ],
        )
