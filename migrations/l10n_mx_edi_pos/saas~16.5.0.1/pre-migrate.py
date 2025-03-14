from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_order", "l10n_mx_edi_is_cfdi_needed", "bool")
    util.create_column(
        cr, "pos_order", "l10n_mx_edi_cfdi_attachment_id", "int4", fk_table="ir_attachment", on_delete_action="SET NULL"
    )
    util.create_column(cr, "pos_order", "l10n_mx_edi_cfdi_state", "varchar")
    util.create_column(cr, "pos_order", "l10n_mx_edi_cfdi_sat_state", "varchar")
    util.create_column(cr, "pos_order", "l10n_mx_edi_cfdi_uuid", "varchar")

    util.explode_execute(
        cr,
        """
            UPDATE pos_order
            SET l10n_mx_edi_is_cfdi_needed = TRUE
            FROM res_company company
            JOIN res_currency curr ON curr.id = company.currency_id
            JOIN res_country country ON country.id = company.account_fiscal_country_id
            WHERE
                company.id = pos_order.company_id
                AND country.code = 'MX'
                AND curr.name = 'MXN'
        """,
        table="pos_order",
    )
