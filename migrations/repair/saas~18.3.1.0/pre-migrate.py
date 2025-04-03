from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "repair.action_repair_picking_type_kanban")
    util.remove_record(cr, "repair.action_repair_overview")
    util.remove_view(cr, "repair.view_repair_tag_form")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "repair.repair_picking_type_menu"),
        ],
    )
