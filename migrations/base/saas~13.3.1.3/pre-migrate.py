# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_timesheets"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_project"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_inventory"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,inventory}_purchase"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,manufacturing}_maintenance"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations_inventory,inventory}_delivery"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,productivity}_documents"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_helpdesk"))
    util.rename_xmlid(cr, *eb("base.module_category_{operations,services}_field_service"))
    util.rename_xmlid(cr, *eb("base.module_category_manufacturing_{plm,product_lifecycle_management_(plm)}"))
    util.rename_xmlid(cr, *eb("base.module_category_{localization,accounting_localizations}"))
    util.rename_xmlid(cr, *eb("base.module_category_sales_{subscription,subscriptions}"))
    util.rename_xmlid(cr, *eb("base.module_category_marketing_{social,social_marketing}"))
    util.rename_xmlid(cr, *eb("base.module_category_{accounting,human_resources}_expense"))
    util.rename_xmlid(cr, *eb("base.module_category_accounting_{payment,payment_acquirers}"))
    util.rename_xmlid(cr, *eb("base.module_category_{discuss,productivity_discuss}"))

    # categories moved to `hidden/` prefix may already exists, deduplicate them
    for cat in {"tools", "tests"}:
        root_name = f"base.module_category_{cat}"
        hidden_name = f"base.module_category_hidden_{cat}"
        root_id = util.ref(cr, root_name)
        hidden_id = util.ref(cr, hidden_name)
        if root_id and hidden_id:
            if root_id != hidden_id:
                util.replace_record_references(
                    cr, ("ir.module.category", root_id), ("ir.module.category", hidden_id), replace_xmlid=False
                )
            cr.execute("DELETE FROM ir_model_data WHERE module=%s AND name=%s", root_name.split("."))
        elif root_id:
            util.rename_xmlid(cr, root_name, hidden_name)

    util.remove_view(cr, "base.view_partner_short_form")

    util.remove_field(cr, "res.partner.bank", "qr_code_valid")
    util.remove_field(cr, "account.setup.bank.manual.config", "qr_code_valid")
