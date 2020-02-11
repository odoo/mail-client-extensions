# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # account_id and refund_account_id have been unset on taxes
    # - tax_eu_sale_skr04
    # - tax_export_skr04
    # - tax_not_taxable_skr04
    # in odoo/odoo@a3bc08d9d8aa40e8d41f99e5b102997c6990396a
    tax_template_ids = tuple(filter(None, (util.ref(cr, 'l10n_de_skr04.%s' % xml_id) for xml_id in [
        'tax_eu_sale_skr04',
        'tax_export_skr04',
        'tax_not_taxable_skr04'
    ])))
    if tax_template_ids:
        cr.execute("""
            UPDATE account_tax_template SET account_id = NULL, refund_account_id = NULL WHERE id in %s
        """, (tax_template_ids,))
    # account.account.template xml_ids have been renamed from account_% to chart_skr04_%
    # in odoo/odoo@a3bc08d9d8aa40e8d41f99e5b102997c6990396a
    # But if they upgraded the module before the migration, they could land with both kind of xml_ids,
    # and duplicate account templates. We therefore take care to rename the xml_ids if they do not exist yet.
    cr.execute("""
        WITH to_rename AS (
            SELECT md1.id, 'chart_skr04_' || ltrim(split_part(md1.name, '_', 2), '0') as name
              FROM ir_model_data md1
              LEFT JOIN ir_model_data md2
                ON (md2.module = md1.module AND md2.name = 'chart_skr04_' || ltrim(split_part(md1.name, '_', 2), '0'))
             WHERE md1.module = 'l10n_de_skr04'
               AND md1.name like 'account\_%'
               AND md1.model = 'account.account.template'
               AND md2.name IS NULL
        )
        UPDATE ir_model_data
           SET name = to_rename.name
          FROM to_rename WHERE to_rename.id = ir_model_data.id
    """)
