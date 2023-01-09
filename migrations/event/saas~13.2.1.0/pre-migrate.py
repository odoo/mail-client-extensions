# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.move_model(cr, "event.event.ticket", "event_sale", "sale")

    if (
        util.module_installed(cr, "event_sale")
        and util.table_exists(cr, "event_event_ticket")
        and not util.table_exists(cr, "event_type_ticket")
    ):
        cr.execute(
            """
            CREATE TABLE event_type_ticket (
                id SERIAL PRIMARY KEY,
                create_uid integer,
                create_date timestamp,
                write_uid integer,
                write_date timestamp,

                name varchar,
                description text,
                event_type_id integer,
                seats_availability varchar,
                seats_max integer,
                product_id integer,
                price numeric
            )
        """
        )
        # NOTE: keep the same id to facilitate the translation convertion
        cr.execute(
            """
            INSERT INTO event_type_ticket(
                id, create_uid, create_date, write_uid, write_date,
                name, event_type_id, seats_availability, seats_max,
                product_id, price
            )
            SELECT id, create_uid, create_date, write_uid, write_date,
                   name, event_type_id, seats_availability, seats_max,
                   product_id, COALESCE(price, 0)
              FROM event_event_ticket
             WHERE event_type_id IS NOT NULL
        """
        )
        cr.execute("SELECT COALESCE(max(id), 0) + 1 FROM event_type_ticket")
        cr.execute("ALTER SEQUENCE event_type_ticket_id_seq RESTART WITH %s", cr.fetchone())
        cr.execute(
            """
            UPDATE ir_translation
               SET name = 'event.type.ticket,name'
             WHERE name = 'event.event.ticket,name'
               AND res_id IN (SELECT id FROM event_type_ticket)
        """
        )
        cr.execute(
            """
            DELETE FROM event_event_ticket
                  WHERE id IN (SELECT id FROM event_type_ticket)
                     OR event_id IS NULL
        """
        )

        util.create_column(cr, "event_event_ticket", "start_sale_date", "date")
        cr.execute("UPDATE event_event_ticket SET start_sale_date = create_date")
        util.rename_field(cr, "event.event.ticket", "deadline", "end_sale_date")

        for move_back in ["product_id", "price", "price_reduce", "price_reduce_taxinc"]:
            util.move_field_to_module(cr, "event.event.ticket", move_back, "event", "event_sale")

    move_fields = {
        "event.type": [("use_ticket", "use_ticketing", "boolean"), ("event_type_ticket_ids", "event_ticket_ids", None)],
        "event.event": [("event_ticket_ids", None, None)],
        "event.registration": [("event_ticket_id", None, "integer")],
    }
    for model, changes in move_fields.items():
        for (field_name, renamed_from, column_type) in changes:
            if renamed_from:
                util.rename_field(cr, model, renamed_from, field_name)
            if column_type:
                table = util.table_of_model(cr, model)
                util.create_column(cr, table, field_name, column_type)
            util.move_field_to_module(cr, model, field_name, "event_sale", "event")

    # Other "normal" changes
    util.create_column(cr, "event_event", "note", "text")
    util.create_column(cr, "event_event", "kanban_state", "varchar")
    util.create_column(cr, "event_event", "kanban_state_label", "varchar")
    util.create_column(cr, "event_event", "stage_id", "integer")  # filled in `post-`
    util.remove_field(cr, "event.event", "state", drop_column=False)  # will be used to fill `stage_id`

    util.create_column(cr, "event_registration", "event_ticket_id", "integer")

    moved_xmlids = """
        event_type_data_{sale,ticket}
        {,event_}event_ticket_form_view
        access_event_event_ticket_user
        access_event_event_ticket_{admin,manager}

        # TODO rename demo data
    """
    for xid in util.splitlines(moved_xmlids):
        source, target = util.expand_braces(xid) if "{" in xid else (xid, xid)
        util.rename_xmlid(cr, f"event_sale.{source}", f"event.{target}")

    # remove wizard
    # Some people link `event.mail` records to templates bound to this wizard.
    # Break the `ondelete=restrict` by explictly removing these `event.mail` record
    # XXX should this be done by `util.remove_model`?
    cr.execute(
        """
        SELECT id
          FROM event_mail
         WHERE template_id IN (SELECT id FROM mail_template WHERE model = 'event.confirm')
    """
    )
    for (em_id,) in cr.fetchall():
        util.remove_record(cr, ("event.mail", em_id))

    util.remove_model(cr, "event.confirm")
