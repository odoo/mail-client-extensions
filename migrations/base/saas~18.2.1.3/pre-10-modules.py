from odoo.upgrade import util


def migrate(cr, version):
    for module in ["l10n_in_gstin_status", "l10n_in_withholding", "l10n_in_reports_gstr", "l10n_in_enet_batch_payment"]:
        util.ENVIRON[module] = util.module_installed(cr, module)

    util.merge_module(cr, "l10n_in_gstin_status", "l10n_in")
    util.merge_module(cr, "l10n_in_withholding", "l10n_in")

    if util.has_enterprise():
        util.rename_module(cr, "pos_l10n_se", "l10n_se_pos")
        util.merge_module(cr, "l10n_ke_hr_payroll_shif", "l10n_ke_hr_payroll")
        util.remove_module(cr, "l10n_in_documents")
        util.merge_module(cr, "l10n_in_asset", "l10n_in_reports")
        util.merge_module(cr, "l10n_in_enet_batch_payment", "l10n_in_reports")
        util.merge_module(cr, "l10n_in_qr_code_bill_scan", "l10n_in_reports")
        util.merge_module(cr, "l10n_in_reports_gstr", "l10n_in_reports")
        util.merge_module(cr, "l10n_in_reports_tds_tcs", "l10n_in_reports")

    if util.module_installed(cr, "pos_iot"):
        modules_to_install = set()
        cr.execute("SELECT 1 FROM ir_config_parameter WHERE key='pos_iot.ingenico_payment_terminal'")
        if cr.rowcount:
            modules_to_install |= {"pos_iot_ingenico"}
        cr.execute("SELECT 1 FROM ir_config_parameter WHERE key='pos_iot.worldline_payment_terminal'")
        if cr.rowcount:
            modules_to_install |= {"pos_iot_worldline"}
        if modules_to_install:
            util.modules_auto_discovery(cr, force_installs=modules_to_install)

    if util.module_installed(cr, "pos_six") and not util.module_installed("pos_iot"):
        util.add_to_migration_reports(
            category="Point of Sale",
            message="""
                    The "Six" module has been removed as it has been deprecated since Odoo 16 due to Six API limits.
                    The alternative is to use "POS IoT Six" module. You can install it in your upgraded DB, or install "IoT for PoS" in your current DB before the upgrade then request a new upgrade.
                    """,
        )
    if util.modules_installed(cr, "pos_iot", "pos_six"):
        util.force_install_module(cr, "pos_iot_six")
    util.remove_module(cr, "pos_six")
    util.merge_module(cr, "payment_razorpay_oauth", "payment_razorpay")
    util.force_migration_of_fresh_module(cr, "stock_maintenance")

    util.merge_module(cr, "l10n_it_edi_ndd", "l10n_it_edi")
