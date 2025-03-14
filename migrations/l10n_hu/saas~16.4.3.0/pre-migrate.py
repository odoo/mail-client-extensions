from odoo.upgrade import util


def migrate(cr, version):
    query = """
               UPDATE account_move m
                  SET delivery_date = move.invoice_date
                 FROM account_move move
                 JOIN res_company company ON move.company_id = company.id
                 JOIN res_country country ON company.account_fiscal_country_id = country.id
                WHERE move.state = 'posted'
                  AND country.code = 'HU'
                  AND move.move_type IN ('out_invoice', 'out_refund')
                  AND move.delivery_date IS NULL
            """
    util.explode_execute(cr, query, table="account_move", alias="m")
