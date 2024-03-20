from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "room.group_room_manager", noupdate=False)
    util.remove_record(cr, "room.module_category_room")
