# ruff: noqa: ERA001
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.partner", "l10n_mx_edi_no_tax_breakdown", "l10n_mx_edi_ieps_breakdown")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_tax_object", "varchar")

    # Mimic the code computing the tax object in the CFDI:
    # The tax object in the CFDI is given by doing:
    #       if customer.l10n_mx_edi_no_tax_breakdown:
    #           tax_objected = '03'
    #       elif all(not x['tax_ids'] for x in base_lines):
    #           tax_objected = '01'
    #       else:
    #           tax_objected = '02'
    # The tax object per line is given by doing:
    #       if line['discount'] != 100.0 and any(tax.l10n_mx_tax_type != 'local' for tax in line['tax_ids']):
    #           line['objeto_imp'] = tax_objected
    #       else:
    #           line['objeto_imp'] = '01'

    query = """
        WITH account_move_line_with_tax_ids AS (
            SELECT line.id AS aml_id,
                   CASE
                       WHEN customer.type = 'invoice' THEN customer.l10n_mx_edi_ieps_breakdown
                       ELSE commercial_customer.l10n_mx_edi_ieps_breakdown
                   END AS tax_breakdown,
                   line.discount = 100 OR COUNT(tax.id) = 0 AS is_01
              FROM account_move_line line
                -- self.is_invoice()
              JOIN account_move move
                ON move.id = line.move_id
               AND move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
              JOIN res_company company
                ON company.id = move.company_id
                -- self.country_code == 'MX'
              JOIN res_country country
                ON country.id = company.account_fiscal_country_id
               AND country.code = 'MX'
                -- self.company_currency_id.name == 'MXN'
              JOIN res_currency currency
                ON currency.id = company.currency_id
               AND currency.name = 'MXN'
               -- customer = customer if customer.type == 'invoice' else customer.commercial_partner_id
              JOIN res_partner customer
                ON customer.id = move.partner_id
              JOIN res_partner commercial_customer
                ON commercial_customer.id = customer.commercial_partner_id
         LEFT JOIN account_move_line_account_tax_rel tax_rel
                ON tax_rel.account_move_line_id = line.id
               AND line.discount != 100
         LEFT JOIN account_tax tax
                ON tax.id = tax_rel.account_tax_id
               AND tax.l10n_mx_tax_type != 'local'
             WHERE line.display_type = 'product'
               AND {parallel_filter}
          GROUP BY line.id, customer.id, commercial_customer.id
        )
        UPDATE account_move_line line
           SET l10n_mx_edi_tax_object = CASE
                   WHEN sub.is_01 THEN '01'
                   WHEN sub.tax_breakdown THEN '03'
                   ELSE '02'
               END
          FROM account_move_line_with_tax_ids sub
         WHERE line.id = sub.aml_id
    """
    util.explode_execute(cr, query, table="account_move_line", alias="line")
