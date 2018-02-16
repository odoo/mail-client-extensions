# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'rating_rating', 'parent_res_name', 'varchar')
    util.create_column(cr, 'rating_rating', 'parent_res_model_id', 'int4')
    util.create_column(cr, 'rating_rating', 'parent_res_model', 'varchar')
    util.create_column(cr, 'rating_rating', 'parent_res_id', 'int4')

    # fill parents...
    parents = {
        'project.task': ('project.project', 'project_id'),
        'project.issue': ('project.project', 'project_id'),
        'mail.channel': ('im_livechat.channel', 'livechat_channel_id'),
        'helpdesk.ticket': ('helpdesk.team', 'team_id'),
    }
    Models = util.env(cr)['ir.model']
    for model, (parent_model, parent_field) in parents.items():
        table = util.table_of_model(cr, model)
        if not util.column_exists(cr, table, parent_field):
            continue
        parent_model_id = Models._get_id(parent_model)
        cr.execute("""
            UPDATE rating_rating r
               SET parent_res_model_id = %s,
                   parent_res_model = %s,
                   parent_res_id = p.{0}
              FROM "{1}" p
             WHERE r.res_model = %s
               AND p.id = r.res_id
        """.format(parent_field, table), [parent_model_id, parent_model, model])

    cr.execute("""
        UPDATE rating_rating
           SET parent_res_name = CONCAT(parent_res_model, '/', parent_res_id)
         WHERE parent_res_model IS NOT NULL
    """)

    util.create_column(cr, 'rating_rating', 'rating_text', 'varchar')
    cr.execute("""
        UPDATE rating_rating
           SET rating_text = CASE WHEN rating >= 7 THEN 'satisfied'
                                  WHEN rating > 3 THEN 'not_satisfied'
                                  WHEN rating >= 1 THEN 'highly_dissatisfied'
                                  ELSE 'no_rating'
                              END
    """)

    util.create_column(cr, 'mail_message', 'rating_value', 'float8')
    cr.execute("""
        UPDATE mail_message m
           SET rating_value = r.rating
          FROM rating_rating r
         WHERE r.message_id = m.id
           AND r.consumed = true
    """)
    # let other messages with NULL rating_value. ORM handle it correctly.
