# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        INSERT INTO account_tax_account_tag(account_tax_id, account_account_tag_id)
             SELECT tax.id, tag.account_account_tag_id
               FROM account_tax as tax
          LEFT JOIN account_tax_template as template
                 ON tax.name = template._old_name AND tax.type_tax_use = template.type_tax_use
               JOIN account_account_tag_account_tax_template_rel as tag
                 ON template.id = tag.account_tax_template_id
             EXCEPT
             SELECT account_tax_id, account_account_tag_id
               FROM account_tax_account_tag
        """)

    util.remove_column(cr, 'account_tax_template', '_old_name')
