from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="res.partner", fieldname="duplicated_bank_account_partners_count")
    util.remove_field(cr, model="res.company", fieldname="account_sale_receipt_tax_id")
    util.remove_field(cr, model="res.company", fieldname="account_purchase_receipt_tax_id")
    util.remove_field(cr, "account.tax", "name_searchable")

    util.create_column(cr, "account_move_line", "no_followup", "bool")
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET no_followup = True
          FROM account_move m
         WHERE l.move_id = m.id
           AND m.move_type = 'entry'
           AND m.origin_payment_id IS NULL
        """,
        table="account_move_line",
        alias="l",
    )
    util.remove_field(cr, "res.config.settings", "module_l10n_eu_oss")

    cr.execute(
        """
        UPDATE res_company
           SET account_storno = true
          FROM res_country
         WHERE res_country.id = res_company.account_fiscal_country_id
           AND res_country.code IN ('BA', 'CN', 'CZ', 'HR', 'PL', 'RO', 'RS', 'RU', 'SI', 'SK', 'UA')
        """,
    )

    util.create_column(cr, "account_move_line", "is_storno", "boolean")
    query = """
        UPDATE account_move_line AS aml
           SET is_storno = true
          FROM account_move AS am
         WHERE aml.move_id = am.id
           AND am.is_storno
        """
    util.explode_execute(cr, query, table="account_move_line", alias="aml")

    util.make_field_non_stored(cr, "account.move", "is_storno", selectable=False)
