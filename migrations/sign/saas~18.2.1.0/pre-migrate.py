from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.cancel_sign_request_item_with_confirmation")
    util.remove_view(cr, "sign.canceled_sign_request_item")

    # Drop the color field of roles as it is not used anymore.
    util.remove_field(cr, "sign.item.role", "color")

    # Remove unique name for roles constrait, menu and action.
    util.remove_constraint(cr, "sign_item_role", "sign_item_role_name_uniq")
    util.remove_menus(cr, [util.ref(cr, "sign.sign_item_role_menu")])
    util.remove_record(cr, "sign.sign_item_role_action")
