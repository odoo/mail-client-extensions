# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # for all fields that have been copied from an old model to a new one
    # we have to update the ir_server_object_lines table with new field ids.
    for suffix in ["", ".line"]:
        src_model = "account.invoice%s" % suffix
        dst_model = "account.move%s" % suffix

        util.update_server_actions_fields(cr, src_model, dst_model)

        # at the same time, update all server actions of these models
        cr.execute(
            """
            UPDATE ir_act_server
               SET model_name = %s, model_id = ir_model.id
              FROM ir_model
             WHERE ir_model.model = %s
               AND ir_act_server.model_name = %s
            """,
            [dst_model, dst_model, src_model],
        )

    # For the 'account.invoice' model some field names have changed, so the following mapping list is used.
    field_name_mapping = [
        ("reference", "invoice_payment_ref"),
        ("vendor_display_name", "invoice_partner_display_name"),
        ("date_invoice", "invoice_date"),
        ("date_due", "invoice_date_due"),
        ("origin", "invoice_origin"),
        ("payments_widget", "invoice_payments_widget"),
        ("payment_term_id", "invoice_payment_term_id"),
    ]
    invoice_move_line_field_map = [
        ("invoice_id", "move_id"),
        ("uom_id", "product_uom_id"),
        ("invoice_line_tax_ids", "tax_ids"),
        ("account_analytic_id", "analytic_account_id"),
    ]

    util.update_server_actions_fields(
        cr, src_model="account.invoice", dst_model="account.move", fields_mapping=field_name_mapping
    )
    util.update_server_actions_fields(
        cr, src_model="account.invoice.line", dst_model="account.move.line", fields_mapping=invoice_move_line_field_map
    )
    for old, new in invoice_move_line_field_map:
        util.update_field_references(cr, old, new, ("account.move.line",))
    for old, new in field_name_mapping:
        util.update_field_references(cr, old, new, ("account.move",))

    # for all fields from 'account.invoice' that have no equivalent in 'account.move'
    # we remove all the corresponding rows in ir_server_object_lines.
    cr.execute(
        """
        DELETE
          FROM ir_server_object_lines l
         USING ir_model_fields mf
         WHERE mf.id = l.col1
           AND mf.model = 'account.invoice'
        """
    )
