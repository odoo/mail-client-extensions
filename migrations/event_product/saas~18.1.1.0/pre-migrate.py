from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.move_field_to_module(cr, "event.registration", "sale_status", "event_sale", "event_product")
    util.create_column(cr, "event_registration", "sale_status", "varchar", default="free")
    util.rename_xmlid(cr, *eb("{event_sale,event_product}.event_registration_view_graph"))
