from odoo.upgrade import util


def _l10n_in_enable_feature(cr, column):
    util.create_column(cr, "res_company", column, "boolean")
    query = util.format_query(
        cr,
        """
        UPDATE res_company company
           SET {column} = true
          FROM res_country country
         WHERE country.id = company.account_fiscal_country_id
           AND country.code = 'IN'
        """,
        column=column,
    )
    cr.execute(query)


def migrate(cr, version):
    _l10n_in_enable_feature(cr, "l10n_in_is_gst_registered")
    if util.ENVIRON.get("l10n_in_gstin_status"):
        _l10n_in_enable_feature(cr, "l10n_in_gstin_status_feature")
    is_withholding_enabled = util.ENVIRON.get("l10n_in_withholding")
    if is_withholding_enabled:
        _l10n_in_enable_feature(cr, "l10n_in_tds_feature")
        _l10n_in_enable_feature(cr, "l10n_in_tcs_feature")
    util.create_column(cr, "account_account", "l10n_in_tds_feature_enabled", "boolean", default=is_withholding_enabled)
    util.create_column(cr, "account_account", "l10n_in_tcs_feature_enabled", "boolean", default=is_withholding_enabled)
    if util.ENVIRON.get("l10n_in_enet_batch_payment"):
        util.create_m2m(cr, "account_batch_payment_ir_attachment_rel", "account_batch_payment", "ir_attachment")
        cr.execute(
            """
            INSERT INTO account_batch_payment_ir_attachment_rel(account_batch_payment_id, ir_attachment_id)
                 SELECT ia.res_id, ia.id
                   FROM ir_attachment ia
                   JOIN account_batch_payment abp
                     ON abp.id = ia.res_id
                    AND ia.res_model = 'account.batch.payment'
                   JOIN res_company company
                     ON company.id = ia.company_id
                   JOIN res_country country
                     ON country.id = company.account_fiscal_country_id
                  WHERE country.code = 'IN'
            """
        )
        util.remove_field(cr, "ir.attachment", "can_be_deleted")
        _l10n_in_enable_feature(cr, "l10n_in_enet_vendor_batch_payment_feature")

    util.remove_view(cr, "l10n_in.res_config_settings_view_form_inherit_l10n_in_withholding")
    util.remove_view(cr, "l10n_in.view_tax_form_inherited_l10n_in_withholding")
    util.remove_view(cr, "l10n_in.view_move_line_tree_l10n_in")
    util.remove_view(cr, "l10n_in.account_move_view_form_inherit_l10n_in_withholding")
    util.remove_view(cr, "l10n_in.move_form_inherit_l10n_in_gst_verification")
    util.remove_field(cr, "res.config.settings", "module_l10n_in_enet_batch_payment")
    util.remove_field(cr, "res.config.settings", "module_l10n_in_withholding")
    util.remove_field(cr, "res.config.settings", "module_l10n_in_gstin_status")
