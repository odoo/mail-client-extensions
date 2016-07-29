# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    tag_61 = util.ref(cr, 'l10n_be.tax_tag_61')
    tag_62 = util.ref(cr, 'l10n_be.tax_tag_62')

    cr.execute("""
        UPDATE account_tax tax
           SET tax_adjustment = true
          FROM account_tax_account_tag tag
         WHERE tax.id = tag.account_tax_id
           AND tag.account_account_tag_id IN %s
    """, [(tag_61, tag_62)])
