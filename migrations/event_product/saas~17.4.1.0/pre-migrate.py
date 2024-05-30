from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    # addons/event_product/data/event_product_data.xml
    util.rename_xmlid(cr, *eb("event_{sale,product}.product_category_events"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.product_product_event"))
    # addons/event_product/data/event_product_demo.xml
    util.rename_xmlid(cr, *eb("event_{sale,product}.product_product_event_standard"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.product_product_event_vip"))
    # addons/event_product/views/event_ticket_views.xml
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_event_ticket_form_view"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_event_ticket_view_kanban_from_event"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_event_ticket_view_form_from_event"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_event_ticket_view_tree_from_event"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_type_ticket_view_form_from_type"))
    util.rename_xmlid(cr, *eb("event_{sale,product}.event_type_ticket_view_tree_from_type"))
    # addons/event_product/models/event_event.py
    util.move_field_to_module(cr, "event.event", "currency_id", "event_sale", "event_product")
    # addons/event_product/models/event_type_ticket.py
    util.move_field_to_module(cr, "event.type.ticket", "description", "event_sale", "event_product")
    util.move_field_to_module(cr, "event.type.ticket", "product_id", "event_sale", "event_product")
    util.move_field_to_module(cr, "event.type.ticket", "currency_id", "event_sale", "event_product")
    util.move_field_to_module(cr, "event.type.ticket", "price", "event_sale", "event_product")
    util.move_field_to_module(cr, "event.type.ticket", "price_reduce", "event_sale", "event_product")
    # addons/event_product/models/event_event_ticket.py
    util.move_field_to_module(cr, "event.event.ticket", "price_reduce_taxinc", "event_sale", "event_product")
    util.move_field_to_module(cr, "event.event.ticket", "price_incl", "event_sale", "event_product")
    # addons/event_product/models/product_product.py
    util.move_field_to_module(cr, "product.product", "event_ticket_ids", "event_sale", "event_product")
