# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""INSERT INTO account_tax_account_tag(account_tax_id, account_account_tag_id)
                  SELECT tax.id, tag.account_account_tag_id
                  FROM account_tax as tax
                  LEFT JOIN account_tax_template as template ON tax.name = template.name AND tax.type_tax_use = template.type_tax_use
                  LEFT JOIN account_account_tag_account_tax_template_rel as tag ON template.id = tag.account_tax_template_id
                  WHERE tag.account_tax_template_id IS NOT NULL
        """)
