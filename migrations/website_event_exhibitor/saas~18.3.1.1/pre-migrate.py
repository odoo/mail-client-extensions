from odoo.upgrade.util import remove_field


def migrate(cr, version):
    remove_field(cr, "event.sponsor", "chat_room_id")
    remove_field(cr, "event.sponsor", "room_name")
