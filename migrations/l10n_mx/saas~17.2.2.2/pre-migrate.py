import itertools


def migrate(cr, version):
    tax_names = [
        "ieps_8_purchase",
        "ieps_8_sale",
        "ieps_25_purchase",
        "ieps_25_sale",
        "ieps_26_5_purchase",
        "ieps_26_5_sale",
        "ieps_30_purchase",
        "ieps_30_sale",
        "ieps_53_purchase",
        "ieps_53_sale",
        "mx_wh_1_25",
        "tax1",
        "tax2",
        "tax3",
        "tax5",
        "tax7",
        "tax8",
        "tax9",
        "tax12",
        "tax13",
        "tax14",
        "tax16",
        "tax17",
        "tax19",
        "tax20",
    ]
    cr.execute("SELECT id FROM res_company WHERE chart_template = 'mx'")
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
