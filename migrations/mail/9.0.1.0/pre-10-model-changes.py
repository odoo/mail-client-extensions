# -*- coding: utf-8 -*-
from uuid import uuid4
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    renames = {
        'group_all_employees': 'channel_all_employees',
        'access_mail_group_all': 'access_mail_channel_all',
        'access_mail_group_user': 'access_mail_channel_user',
        # 'mail_group_public_and_joined': 'mail_channel_rule',      # no rename, force update
        'action_mail_group_feeds': 'mail_channel_action_timeline',
        'view_group_kanban': 'mail_channel_view_kanban',
        'view_group_form': 'mail_channel_view_form',
        'view_group_tree': 'mail_channel_view_tree',
        'view_group_search': 'mail_channel_view_search',
        'action_view_groups': 'mail_channel_action_view',
        'mail_group_root': 'mail_channel_menu_root',
        'mail_allgroups': 'mail_channel_menu_all',

        # demo data, just in case
        'group_best_sales_practices': 'channel_1',
        'group_board': 'channel_2',
        'group_rd': 'channel_3',
        'msg_group_1_1': 'mail_message_channel_1_1',
        'msg_group_1_2': 'mail_message_channel_1_2',
        'msg_group_1_3': 'mail_message_channel_1_2_1',
        'msg_empl_1': 'mail_message_channel_whole_2',
        'msg_empl_1_2': 'mail_message_channel_whole_2_1',
        'msg_empl_1_3': 'mail_message_channel_whole_2_2',
        'msg_board_1': 'mail_message_channel_2_1',
    }
    for f, t in renames.iteritems():
        util.rename_xmlid(cr, 'mail.' + f, 'mail.' + t)

    removes = util.splitlines("""
        mail_group_public_and_joined
        mail_followers_read_write_others
        mail_followers_read_write_own
        mail_message_read_partner_or_author
        action_client_messaging_menu
    """)
    for rem in removes:
        util.remove_record(cr, 'mail.' + rem)

    util.remove_view(cr, 'mail.view_users_form_mail')
    util.remove_view(cr, 'mail.res_partner_opt_out_form')

    util.drop_depending_views(cr, 'mail_message', 'model')
    cr.execute("UPDATE mail_message SET type='email' WHERE type IS NULL AND message_id IS NOT NULL")
    cr.execute("UPDATE mail_message SET type='comment' WHERE type IS NULL")

    # The field `message_follower_ids` now point to new model `mail.follower`
    # Replace references to point to the new `message_partner_ids` (for domains)
    util.update_field_usage(cr, "mail.thread", "message_follower_ids", "message_partner_ids")

    util.rename_model(cr, 'mail.group', 'mail.channel')
    cr.execute(
        'ALTER TABLE mail_group_res_group_rel RENAME COLUMN mail_group_id TO mail_channel_id')
    cr.execute('ALTER TABLE mail_group_res_group_rel RENAME TO mail_channel_res_group_rel')

    util.create_column(cr, 'mail_channel', 'uuid', 'varchar')
    cr.execute('SELECT id FROM mail_channel WHERE "uuid" IS NULL')
    for chan, in cr.fetchall():
        cr.execute('UPDATE mail_channel SET "uuid"=%s WHERE id=%s', [str(uuid4()), chan])

    util.create_column(cr, 'mail_channel', 'email_send', 'boolean')
    cr.execute("UPDATE mail_channel SET email_send=true")

    # Remove FK with ON DELETE CASCASE since we want to keep the mail.channel records
    cr.execute("ALTER TABLE mail_channel DROP CONSTRAINT mail_channel_menu_id_fkey")
    cr.execute("DELETE FROM ir_ui_menu WHERE id IN (SELECT menu_id FROM mail_channel)")
    cr.execute("ALTER TABLE mail_channel DROP COLUMN menu_id")

    # link partners to channels
    cr.execute("""
        CREATE TABLE mail_channel_partner(
            id SERIAL PRIMARY KEY,
            partner_id integer,
            channel_id integer,
            seen_message_id integer,
            fold_state varchar
        )
    """)
    cr.execute("""
        INSERT INTO mail_channel_partner(partner_id, channel_id, fold_state, seen_message_id)
        SELECT f.partner_id, f.res_id, 'closed',
               (SELECT max(m.id)
                  FROM mail_message m
                  JOIN mail_notification n ON (n.message_id = m.id AND n.partner_id = f.partner_id)
                 WHERE f.res_model = m.model
                   AND f.res_id = m.res_id
                   AND n.is_read = true
     )
          FROM mail_followers f
         WHERE res_model = 'mail.channel'
      GROUP BY partner_id, res_model, res_id
    """)
    cr.execute("DELETE FROM mail_followers WHERE res_model='mail.channel'")

    # link messages to channels
    util.create_m2m(cr, 'mail_message_mail_channel_rel', 'mail_message', 'mail_channel')
    cr.execute("""
        INSERT INTO mail_message_mail_channel_rel(mail_channel_id, mail_message_id)
        SELECT res_id, id
          FROM mail_message
         WHERE model='mail.channel'
    """)

    # mail messages & notifications
    util.create_m2m(cr, 'mail_message_res_partner_starred_rel', 'mail_message', 'res_partner')
    cr.execute("""
        INSERT INTO mail_message_res_partner_starred_rel(mail_message_id, res_partner_id)
             SELECT m.id, n.partner_id
               FROM mail_notification n
               JOIN mail_message m
                 ON m.id = n.message_id
              WHERE n.starred = true
                AND m.type != 'notification'
           GROUP BY 1, 2
    """)
    util.create_m2m(cr, 'mail_message_res_partner_needaction_rel', 'mail_message', 'res_partner')
    cr.execute("""
        INSERT INTO mail_message_res_partner_needaction_rel(mail_message_id, res_partner_id)
             SELECT m.id, n.partner_id
               FROM mail_message m
               JOIN mail_notification n
                 ON n.message_id = m.id
              WHERE n.is_read = false
                AND m.model != 'mail.channel'
           GROUP BY m.id, n.partner_id
    """)

    util.delete_model(cr, 'mail.notification')
    util.delete_model(cr, 'mail.vote')
    cr.execute("DROP INDEX IF EXISTS mail_notification_partner_id_read_starred_message_id")

    if util.table_exists(cr, 'im_chat_shortcode'):
        util.rename_model(cr, 'im_chat.shortcode', 'mail.shortcode')
        util.move_model(cr, 'mail.shortcode', 'im_chat', 'mail', move_data=True)
        util.create_column(cr, 'mail_shortcode', 'shortcode_type', 'varchar')
        cr.execute("UPDATE mail_shortcode SET shortcode_type='image'")
