def migrate(cr, version):
    tax_renames = [
        ("account_tax_template_p_irpf21td", "15% WHI", '"15% WHI monies"'),
        ("account_tax_template_p_irpf21te", "15% WHI cash", '"15% WHI worker cash"'),
    ]
    for imd, name, new_name in tax_renames:
        cr.execute(
            r"""
            UPDATE account_tax t
               SET name = jsonb_set(t.name,'{en_US}',%s)
              FROM ir_model_data d
             WHERE d.model = 'account.tax'
               AND d.res_id = t.id
               AND d.name ~ concat('\d+_', %s)
               AND t.name->>'en_US' = %s
            """,
            [new_name, imd, name],
        )
