# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Normally not necessary to create those fields as the fields come from l10n_co_edi_ubl_2_1 and this module should have been
    # installed to be legally compliant, but you never know
    util.create_column(cr, "account_move", "l10n_co_edi_cufe_cude_ref", "varchar")
    util.create_column(cr, "account_move", "l10n_co_edi_payment_option_id", "int4")
    util.create_column(cr, "account_move", "l10n_co_edi_debit_origin_id", "int4")
    util.create_column(cr, "account_move", "l10n_co_edi_operation_type", "varchar")
    util.create_column(cr, "account_move", "l10n_co_edi_description_code_credit", "varchar")
    util.create_column(cr, "account_move", "l10n_co_edi_description_code_debit", "varchar")
    cr.execute(
        """
            UPDATE account_move
               SET debit_origin_id = l10n_co_edi_debit_origin_id
             WHERE l10n_co_edi_debit_origin_id IS NOT NULL
        """
    )

    util.remove_field(cr, "account.move", "l10n_co_edi_debit_origin_id")

    # Actually not all removed in saas~13.5. Fields on move and journal has been added in 13.0 way after the release.
    # See https://github.com/odoo/enterprise/pull/30022
    models = ("account.tax", "account.move", "account.journal")
    for model in models:
        util.update_field_usage(cr, model, "l10n_co_edi_country_code", "country_code")
        util.remove_field(cr, model, "l10n_co_edi_country_code")

    util.create_column(cr, "account_tax_template", "l10n_co_edi_type", "int4")

    util.create_column(cr, "account_journal", "l10n_co_edi_dian_authorization_end_date", "date")
    util.create_column(cr, "account_journal", "l10n_co_edi_min_range_number", "int4")
    util.create_column(cr, "account_journal", "l10n_co_edi_max_range_number", "int4")
    util.create_column(cr, "account_journal", "l10n_co_edi_debit_note", "boolean")

    util.create_column(cr, "l10n_co_edi_tax_type", "description", "varchar")
    util.create_column(cr, "account_move_reversal", "l10n_co_edi_description_code_credit", "varchar")
    util.create_column(cr, "account_debit_note", "l10n_co_edi_description_code_debit", "varchar")

    util.create_column(cr, "product_template", "l10n_co_edi_customs_code", "varchar")
    # this field is an aberration
    util.create_column(cr, "uom_uom", "l10n_co_edi_country_code", "varchar", default="CO")
    util.create_column(cr, "res_company", "l10n_co_edi_template_code", "varchar")
    util.create_column(cr, "res_partner", "l10n_co_edi_fiscal_regimen", "varchar", default="48")
    util.create_column(cr, "res_partner", "l10n_co_edi_commercial_name", "varchar")

    util.remove_view(cr, "l10n_co_edi.view_account_invoice_refundinherit_l10n_co_edi")
    util.remove_view(cr, "l10n_co_edi.view_partner_property_form_inherit_l10n_co_edi_ubl_2_1")
    util.remove_view(cr, "l10n_co_edi.product_template_only_form_view_inherit_l10n_co_edi_ubl_2_1")
    util.remove_view(cr, "l10n_co_edi.view_account_journal_form_inherit_l10n_co_edi_ubl_2_1")
    util.remove_view(cr, "l10n_co_edi.move_form_inherit_l10n_co_edi_ubl_2_1")
