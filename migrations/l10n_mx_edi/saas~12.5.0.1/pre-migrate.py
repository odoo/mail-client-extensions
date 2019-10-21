# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_mx_edi_cer_source", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_external_trade", "boolean")

    util.create_column(cr, "account_move_line", "l10n_mx_edi_customs_number", "varchar")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_tariff_fraction_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_umt_aduana_id", "int4")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_qty_umt", "float8")
    util.create_column(cr, "account_move_line", "l10n_mx_edi_price_unit_umt", "float8")

    cr.execute(
        """
        UPDATE account_move_line aml
           SET l10n_mx_edi_tariff_fraction_id=p.l10n_mx_edi_tariff_fraction_id,
               l10n_mx_edi_umt_aduana_id=p.l10n_mx_edi_umt_aduana_id
          FROM product_product p
         WHERE aml.product_id=p.id
    """
    )

    util.create_column(cr, "account_payment", "l10n_mx_edi_partner_bank_id", "int4")

    util.create_column(cr, "account_payment_register", "l10n_mx_edi_payment_method_id", "int4")
    util.create_column(cr, "account_payment_register", "l10n_mx_edi_partner_bank_id", "int4")

    util.create_column(cr, "product_template", "l10n_mx_edi_tariff_fraction_id", "int4")
    util.create_column(cr, "product_template", "l10n_mx_edi_umt_aduana_id", "int4")

    util.create_column(cr, "uom_uom", "l10n_mx_edi_code_aduana", "varchar")

    util.create_column(cr, "res_company", "l10n_mx_edi_num_exporter", "varchar")
    util.create_column(cr, "res_company", "l10n_mx_edi_fiscal_regime", "varchar")

    util.create_column(cr, "res_partner", "l10n_mx_edi_external_trade", "boolean")
    util.create_column(cr, "res_partner", "l10n_mx_edi_colony_code", "varchar")
    util.create_column(cr, "res_partner", "l10n_mx_edi_locality_id", "int4")

    util.remove_field(cr, "account.move", "l10n_mx_edi_cfdi_certificate_id")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_cfdi_certificate_id")
    util.remove_field(cr, "account.fiscal.position", "l10n_mx_edi_code")

    util.remove_view(cr, "l10n_mx_edi.res_config_settings_view_form_inherit_l10n_mx_edi_external_trade")
    util.remove_view(cr, "l10n_mx_edi.res_partner_form_inherit_l10n_mx_edi_external_trade")
    util.remove_view(cr, "l10n_mx_edi.report_invoice_documement_external_trade")
