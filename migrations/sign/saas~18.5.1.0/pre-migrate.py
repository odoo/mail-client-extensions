from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "sign_send_request", "signers_count")
    util.create_column(cr, "sign_item_type", "field_size", "varchar", default="regular_text")
    util.create_column(cr, "sign_template", "signature_request_validity", "int", default=60)
    util.create_column(cr, "sign_request", "send_channel", "varchar", default="email")

    cr.execute(
        """
        UPDATE sign_item_type
            SET field_size = CASE
                WHEN default_width <= 0.14 THEN 'short_text'
                WHEN default_width >= 0.24 THEN 'long_text'
                ELSE 'regular_text'
            END
        WHERE item_type = 'text'
        """
    )

    util.make_field_non_stored(cr, "sign.item.type", "default_width", selectable=False)
    util.make_field_non_stored(cr, "sign.item.type", "default_height", selectable=False)
    util.rename_field(cr, "sign.send.request", "message", "body")

    util.delete_unused(cr, "sign.sign_item_role_user", keep_xmlids=False)

    if util.module_installed(cr, "hr_sign"):
        util.rename_xmlid(cr, "sign.sign_item_role_customer", "hr_sign.sign_item_role_default")
        util.rename_xmlid(cr, "sign.sign_item_role_employee", "hr_sign.sign_item_role_employee_signatory")
    else:
        util.delete_unused(cr, "sign.sign_item_role_customer", keep_xmlids=False)
        util.delete_unused(cr, "sign.sign_item_role_employee", keep_xmlids=False)

    util.remove_view(cr, "sign.res_users_view_form")
    util.remove_view(cr, "sign.view_users_form_simple_modif")
