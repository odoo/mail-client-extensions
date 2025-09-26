from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_ke_hr_payroll") and not util.module_installed(cr, "account"):
        # l10n_ke_hr_payroll now depends on l10n_ke that depends on account
        # installing account makes a lot of noise for new computed fields
        # we don not expect real-world DBs to use Kenyan payroll without account
        util.create_column(cr, "res_partner", "invoice_warn", "varchar", default="no-message")
        util.create_column(cr, "res_partner", "supplier_rank", "int4", default=0)
        util.create_column(cr, "res_partner", "customer_rank", "int4", default=0)
        # account_edi_ubl_cii is auto-installed from account
        util.ENVIRON["CI_IGNORE_NO_ORM_TABLE_CHANGE"].update(
            {
                ("res.partner", "ubl_cii_format"),
                ("res.partner", "peppol_endpoint"),
                ("res.partner", "peppol_eas"),
            }
        )
    util.merge_module(cr, "l10n_ke_hr_payroll_bik", "l10n_ke_hr_payroll")
    util.remove_module(cr, "l10n_ae_pos")
    util.remove_module(cr, "purchase_enterprise")
    util.merge_module(cr, "loyalty_delivery", "sale_loyalty_delivery")
    if util.has_enterprise():
        util.merge_module(cr, "sale_timesheet_account_budget", "project_account_budget")
        util.remove_module(cr, "website_sale_renting_comparison")
        util.remove_module(cr, "website_sale_renting_wishlist")
        util.merge_module(cr, "l10n_pl_reports_jpk", "l10n_pl_reports")
        util.remove_module(cr, "l10n_br_avatax_sale")
        util.rename_module(cr, "account_avatax_sale_subscription", "sale_subscription_external_tax")
        util.rename_module(cr, "website_sale_account_avatax", "website_sale_external_tax")

        if util.module_installed(cr, "sale_subscription"):
            util.move_field_to_module(cr, "sale.order", "internal_note", "sale_temporal", "sale_subscription")
            # sale_subscription needs this field for migrations in 16.5 as well
            util.remove_field(cr, "sale.order", "recurrence_id", drop_column=False)

        if util.module_installed(cr, "sale_renting"):
            util.merge_module(cr, "sale_temporal", "sale_renting")
        else:
            if util.module_installed(cr, "sale_subscription"):
                # sale_subscription needs these tables for migrations in 16.5 as well
                util.remove_model(cr, "sale.temporal.recurrence", drop_table=False)
                util.remove_model(
                    cr, "product.pricing", drop_table=False, ignore_m2m=("product_pricing_product_product_rel",)
                )
            util.remove_module(cr, "sale_temporal")

    if util.module_installed(cr, "website_sale_digital"):
        util.move_field_to_module(cr, "ir.attachment", "product_downloadable", "website_sale_digital", "sale")

    util.remove_module(cr, "website_sale_digital")
    util.merge_module(cr, "l10n_it_edi_pa", "l10n_it_edi")

    util.remove_module(cr, "sale_quotation_builder")
    util.merge_module(cr, "event_barcode", "event")
    util.merge_module(cr, "l10n_pl_jpk", "l10n_pl")
    util.remove_module(cr, "l10n_pl_sale_stock")

    if util.has_enterprise():
        util.merge_module(cr, "account_sepa_pain_001_001_09", "account_sepa")
        util.merge_module(cr, "hr_payroll_account_sepa_09", "hr_payroll_account_sepa")
        util.merge_module(cr, "l10n_lu_reports_annual_vat_2023", "l10n_lu_reports")

    util.force_install_module(cr, "base_import_module")

    if util.module_installed(cr, "l10n_in_hr_payroll"):
        # l10n_in_hr_payroll now depends on hr_payroll_holidays that depends (multi-level)
        # on calendar module, the latter adds a new column to res.partner
        util.create_column(cr, "res_partner", "calendar_last_notif_ack", "timestamp", default="now")

    if util.module_installed(cr, "l10n_uy") and not util.module_installed(cr, "base_vat"):
        # l10n_uy now depends on l10n_latam_base that depends on base_vat
        util.force_upgrade_of_fresh_module(cr, "base_vat")
