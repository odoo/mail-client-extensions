from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "web_kanban_gauge", "web")
    util.merge_module(cr, "pos_epson_printer_restaurant", "pos_epson_printer")
    if util.has_enterprise():
        util.merge_module(cr, "pos_restaurant_iot", "pos_iot")
        util.merge_module(cr, "l10n_hk_hr_payroll_hsbc_autopay", "l10n_hk_hr_payroll")

    # l10n_mx cfid 3.0 and 4.0 merge
    util.merge_module(cr, "l10n_mx_edi_stock_extended_40", "l10n_mx_edi_stock_extended")
    util.merge_module(cr, "l10n_mx_edi_stock_40", "l10n_mx_edi_stock")
    util.merge_module(cr, "l10n_mx_edi_extended_40", "l10n_mx_edi_extended")
    util.merge_module(cr, "l10n_mx_edi_40", "l10n_mx_edi")
    util.merge_module(cr, "l10n_pe_edi_stock_20", "l10n_pe_edi_stock")
    util.merge_module(cr, "website_event_questions", "website_event")
    util.merge_module(cr, "website_event_crm_questions", "website_event_crm")
    util.merge_module(cr, "account_reconcile_wizard", "account_accountant")

    if util.table_exists(cr, "note_note"):
        # uninstall the "note" module if it appears unused
        cr.execute(
            """
            SELECT 1
              FROM note_note n
             WHERE NOT EXISTS (SELECT 1
                                 FROM ir_model_data
                                WHERE model = 'note.note'
                                  AND module IN ('note', 'hr_payroll')
                                  AND res_id = n.id)
             LIMIT 1            """
        )
        if not cr.rowcount:
            util.change_field_selection_values(cr, "mail.activity.type", "category", {"reminder": "default"})
            cr.execute(
                """
                DELETE FROM ir_model_data xid
                      USING mail_activity a
                      WHERE xid.model = 'mail.activity.type'
                        AND xid.module = 'note'
                        AND xid.name = 'mail_activity_data_reminder'
                        AND xid.res_id = a.activity_type_id
                """
            )
            util.uninstall_module(cr, "note")
        elif util.on_CI():
            act = util.ref(cr, "project.project_2_activity_1")
            meeting = util.ref(cr, "mail.mail_activity_data_meeting")
            if meeting and not act:
                # if `calendar` is installed but `project` not, the creation of `project` demo data fail.
                # Avoid that by forcing data value.
                cr.execute(
                    "UPDATE mail_activity_type SET category='default' WHERE id=%s AND category='meeting'",
                    [meeting],
                )
    util.rename_module(cr, "note", "project_todo")

    if util.module_installed(cr, "sale_subscription"):
        util.force_migration_of_fresh_module(cr, "account_accountant")
        util.force_migration_of_fresh_module(cr, "account_followup")

    if util.module_installed(cr, "iap_extract") and not util.module_installed(cr, "iap"):
        util.uninstall_module(cr, "iap_extract")

    if util.modules_installed(cr, "hr_holidays", "l10n_fr"):
        util.force_upgrade_of_fresh_module(cr, "l10n_fr_hr_holidays")

    util.force_upgrade_of_fresh_module(cr, "l10n_es_edi_facturae")
