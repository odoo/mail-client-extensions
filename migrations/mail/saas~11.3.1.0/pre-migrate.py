# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_activity", "automated", "boolean")
    cr.execute("UPDATE mail_activity SET automated=false")

    cr.execute("""
      WITH am AS (
        SELECT model,
               array_agg(name) @> ARRAY['activity_date_deadline', 'activity_ids']::varchar[] ac
          FROM ir_model_fields
      GROUP BY model
      )
      SELECT model FROM am WHERE ac=true
    """)
    models = cr.fetchall()
    for model, in models:
        table = util.table_of_model(cr, model)
        util.remove_column(cr, table, "activity_date_deadline")
    cr.execute(
      """
        UPDATE ir_model_fields
           SET store = 'f'
         WHERE model in %s
           AND name = 'activity_date_deadline'
      """, (tuple(models),)
    )

    # short codes
    util.remove_field(cr, "mail.shortcode", "unicode_source")
    util.remove_field(cr, "mail.shortcode", "shortcode_type")

    # TODO? remove shortcodes define in xml? let orm do it?
