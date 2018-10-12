# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "l10n_be_structured_comm", "varchar")
    cr.execute("""
        WITH most_used AS (
            SELECT company_id,
                   (SELECT algo
                      FROM unnest(array_agg(out_inv_comm_algorithm)) as algo
                  GROUP BY algo
                  ORDER BY count(*) DESC
                  LIMIT 1)
              FROM res_partner
             WHERE out_inv_comm_algorithm IS NOT NULL
          GROUP BY company_id
        )
        UPDATE res_company c
           SET l10n_be_structured_comm = COALESCE(p.out_inv_comm_algorithm,
                                                  (SELECT algo FROM most_used WHERE company_id = c.id),
                                                  'random')
          FROM res_partner p
         WHERE p.id = c.partner_id
    """)
    cr.execute("""
        UPDATE res_company c
           SET invoice_reference_type='structured'
         WHERE EXISTS(SELECT 1
                        FROM account_invoice
                       WHERE reference_type='bba'
                         AND "type" = 'out_invoice'
                         AND company_id=c.id)
    """)
    util.remove_field(cr, "res.partner", "out_inv_comm_type")
    util.remove_field(cr, "res.partner", "out_inv_comm_algorithm")

    util.remove_view(cr, "l10n_be_invoice_bba.customer_invoice_bbacomm_form")
    util.remove_view(cr, "l10n_be_invoice_bba.supplier_invoice_bbacomm_form")
    util.remove_view(cr, "l10n_be_invoice_bba.view_partner_inv_comm_type_form")
    util.remove_view(cr, "l10n_be_invoice_bba.report_invoice_document_inherit")
    util.remove_view(cr, "l10n_be_invoice_bba.res_config_settings_view_form_inherit_account_invoicing")
