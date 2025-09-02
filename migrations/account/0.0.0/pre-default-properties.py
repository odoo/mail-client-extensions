# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~17.5"):
        _ensure_default_properties(cr)


def _ensure_default_properties(cr):
    if not util.version_gte("saas~16.1"):  # this branch is for upgrades with target <=16.0
        join = "JOIN account_account_type t ON (t.id = a.user_type_id)"
        condition = "t.type IN ('payable', 'receivable')"
        prop_label = "t.type"
    else:
        join = ""
        condition = "a.account_type IN ('asset_receivable', 'liability_payable')"
        prop_label = "split_part(a.account_type, '_', 2)"

    # ensure each company have a defaults partner properties set
    query = util.format_query(
        cr,
        """
        INSERT INTO ir_property(name, company_id, type, fields_id, value_reference)
        SELECT f.name, a.company_id, 'many2one', f.id, CONCAT('account.account,', (array_agg(a.id ORDER BY a.code))[1])
          FROM account_account a
          {}
          JOIN ir_model_fields f ON (f.model = 'res.partner' AND f.name = CONCAT('property_account_', {}, '_id'))
     LEFT JOIN ir_property p ON (p.fields_id = f.id AND p.company_id = a.company_id AND p.res_id IS NULL)
         WHERE {}
           AND p.id IS NULL
      GROUP BY f.name, a.company_id, f.id
        """,
        util.SQLStr(join),
        util.SQLStr(prop_label),
        util.SQLStr(condition),
    )
    cr.execute(query)

    # If you didn't understand the previous query, here is the equivalent in human readable code
    """
    for company in env["res.company"].search([]):
        for acc_type in ("payable", "receivable"):
            account = env["account.account"].search(
                [("user_type_id.type", "=", acc_type), ("company_id", "=", company.id)], limit=1
            )
            field = env["ir.model.fields"].search(
                [("model", "=", "res.partner"), ("name", "=", "property_account_%s_id" % acc_type)]
            )
            property = env["ir.property"].search(
                [
                    ("name", "=", "property_account_%s_id" % acc_type),
                    ("company_id", "=", company.id),
                    ("fields_id", "=", field.id),
                    ("res_id", "=", None),
                ]
            )
            if account and not property:
                env["ir.property"].create(
                    {
                        "name": "property_account_%s_id" % acc_type,
                        "company_id": company.id,
                        "type": "many2one",
                        "fields_id": field.id,
                        "value_reference": "account.account,%s" % account.id,
                    }
                )
    """
