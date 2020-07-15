# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Convert old event_type_id to event_tag to allow filter on Ecommerce

    util.create_column(cr, "event_tag", "_tmp_old_event_type_id", "int4")

    cr.execute(
        """
        WITH new_parent_cat AS (
            INSERT INTO event_tag_category (name, sequence) VALUES ('Type', 0) RETURNING id
        ),
        new_tag AS (
            INSERT INTO event_tag (_tmp_old_event_type_id, name, sequence, category_id)
                 SELECT id, name, sequence, (select id from new_parent_cat)
                   FROM event_type
              RETURNING id, _tmp_old_event_type_id
        )
        INSERT INTO event_event_event_tag_rel(event_event_id, event_tag_id)
            SELECT e.id, s.id
              FROM event_event e
              JOIN new_tag s ON s._tmp_old_event_type_id = e.event_type_id
    """
    )

    util.remove_column(cr, "event_tag", "_tmp_old_event_type_id")
