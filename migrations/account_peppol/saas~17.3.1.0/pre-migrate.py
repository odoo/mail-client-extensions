from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "res.company",
        "account_peppol_proxy_state",
        {
            "not_verified": "in_verification",
            "sent_verification": "in_verification",
            "pending": "smp_registration",
            "active": "receiver",
            "canceled": "not_registered",
        },
    )
    util.change_field_selection_values(cr, "account.move", "peppol_move_state", {"canceled": None})

    for model, field in [
        ("account.move", "peppol_is_demo_uuid"),
        ("res.company", "is_account_peppol_participant"),
        ("res.config.settings", "account_peppol_endpoint_warning"),
        ("res.config.settings", "account_peppol_verification_code"),
        ("res.config.settings", "is_account_peppol_participant"),
        ("res.config.settings", "account_peppol_edi_mode"),
        ("res.config.settings", "account_peppol_mode_constraint"),
    ]:
        util.remove_field(cr, model, field)

    util.remove_view(cr, "account_peppol.account_peppol_view_in_invoice_bill_tree_inherit")
