from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_preset", "available_in_self", "boolean")
    util.create_column(cr, "pos_preset", "service_at", "varchar", default="table")

    update_query = """
        UPDATE pos_preset p
           SET available_in_self = true,
               service_at = 'counter'
          FROM pos_config c
         WHERE p.id = c.default_preset_id
           AND c.self_ordering_takeaway
    """
    cr.execute(update_query)

    util.remove_field(cr, "pos.config", "self_ordering_takeaway")
    util.remove_field(cr, "res.config.settings", "pos_self_ordering_takeaway")
