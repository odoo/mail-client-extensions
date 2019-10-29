# -*- coding: utf-8 -*-


def migrate(cr, version):
    # ensure each company have a defaults partner properties set
    cr.execute(
        """
        INSERT INTO ir_property(name, company_id, type, fields_id, value_reference)
        SELECT f.name, a.company_id, 'many2one', f.id, CONCAT('account.account,', (array_agg(a.id ORDER BY a.code))[1])
          FROM account_account a
          JOIN account_account_type t ON (t.id = a.user_type_id)
          JOIN ir_model_fields f ON (f.model = 'res.partner' AND f.name = CONCAT('property_account_', t.type, '_id'))
     LEFT JOIN ir_property p ON (p.fields_id = f.id AND p.company_id = a.company_id AND p.res_id IS NULL)
         WHERE t.type IN ('payable', 'receivable')
           AND p.id IS NULL
      GROUP BY f.name, a.company_id, f.id
    """
    )

    # If you didn't understand the previous query, here is the equivalent in human readable code

    # for company in env["res.company"].search([]):
    #     for acc_type in ("payable", "receivable"):
    #         account = env["account.account"].search(
    #             [("user_type_id.type", "=", acc_type), ("company_id", "=", company.id)], limit=1
    #         )
    #         field = env["ir.model.fields"].search(
    #             [("model", "=", "res.partner"), ("name", "=", "property_account_%s_id" % acc_type)]
    #         )
    #         property = env["ir.property"].search(
    #             [
    #                 ("name", "=", "property_account_%s_id" % acc_type),
    #                 ("company_id", "=", company.id),
    #                 ("fields_id", "=", field.id),
    #                 ("res_id", "=", None),
    #             ]
    #         )
    #         if account and not property:
    #             env["ir.property"].create(
    #                 {
    #                     "name": "property_account_%s_id" % acc_type,
    #                     "company_id": company.id,
    #                     "type": "many2one",
    #                     "fields_id": field.id,
    #                     "value_reference": "account.account,%s" % account.id,
    #                 }
    #             )
