from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr, "website_sale_shiprocket.shiprocket_payment_method_cash_on_delivery", deactivate=True, keep_xmlids=False
    )
    util.delete_unused(
        cr, "website_sale_shiprocket.payment_provider_shiprocket_cod", deactivate=True, keep_xmlids=False
    )
    util.remove_module(cr, "website_sale_shiprocket")

    # Remove jitsi related modules:
    util.remove_inherit_from_model(cr, "event.sponsor", "chat.room.mixin")
    util.remove_module(cr, "website_event_jitsi")
    util.remove_module(cr, "website_event_meet")
    util.remove_module(cr, "website_event_meet_quiz")
    util.remove_module(cr, "website_jitsi")
    util.remove_module(cr, "l10n_in_purchase")

    util.merge_module(cr, "sale_async_emails", "sale")

    util.rename_module(cr, "pos_viva_wallet", "pos_viva_com")

    util.merge_module(cr, "pos_preparation_display", "pos_enterprise")
    util.remove_module(cr, "pos_hr_preparation_display")

    if util.has_enterprise():
        util.remove_module(cr, "sale_renting_sign")
        util.rename_module(cr, "pos_restaurant_appointment", "pos_appointment")
        util.merge_module(cr, "sale_commission_linked_achievement", "sale_commission")
        util.remove_module(cr, "test_l10n_ch_hr_payroll_account")
        util.remove_module(cr, "l10n_be_reports_post_wizard")
        util.remove_module(cr, "l10n_nl_reports_vat_pay_wizard")
        # partially merged, some other data moved to l10n_be_hr_payroll see pre- script there
        util.merge_module(cr, "l10n_be_hr_contract_salary_mobility_budget", "l10n_be_hr_contract_salary")

        if util.module_installed(cr, "l10n_in_reports"):
            util.force_install_module(cr, "l10n_in_asset")
            util.force_upgrade_of_fresh_module(cr, "l10n_in_asset")

    util.remove_module(cr, "l10n_br_test_avatax_sale")

    if util.modules_installed(cr, "membership", "website_crm_partner_assign"):
        cr.execute("""
            SELECT id, name
              FROM res_partner r
             WHERE COALESCE(r.membership_stop > NOW() at time zone 'UTC', true)
               AND COALESCE(r.membership_start < NOW() at time zone 'UTC', true)
               AND r.membership_state NOT IN ('none', 'canceled', 'old')
               AND r.grade_id IS NOT NULL
        """)
        total = cr.rowcount
        rows = cr.fetchmany(20)
        if rows:
            util.add_to_migration_reports(
                category="Membership",
                message="""
                    <details>
                        <summary>
                            In Odoo 19, the "Membership" module has dramatically changed.
                            Members are now handled via grades/levels assigned from the contact form or by selling a membership product.
                            The following list show {}partners that already had an assigned grade before upgrade that is not linked to their current membership:
                        </summary>
                        <ul>{}</ul>
                    </details>
                """.format(
                    "(first 20 out of {}) ".format(total) if total > 20 else " ",
                    "".join(
                        "<li>{}</li>".format(util.get_anchor_link_to_record("res.partner", id, name))
                        for id, name in rows
                    ),
                ),
            )

    util.rename_module(cr, "membership", "partnership")
    util.remove_module(cr, "website_membership")
    if util.modules_installed(cr, "l10n_in_ewaybill", "l10n_in_edi"):
        util.force_upgrade_of_fresh_module(cr, "l10n_in_ewaybill_irn")
