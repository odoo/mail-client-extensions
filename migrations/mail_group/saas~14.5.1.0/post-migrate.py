# -*- coding: utf-8 -*-

from odoo.tools import email_normalize

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    # 0. Delete de demo data from <mail.group> to avoid a pk conflict with existing <mail.channel> records
    cr.execute("DELETE FROM mail_group")

    # 1. Create the <mail.group> from the <mail.channel>
    #    And keep the old <mail.channel>.id in a temporary column
    cr.execute(
        """
        INSERT INTO mail_group (
                        id,
                        active,
                        create_uid,
                        create_date,
                        write_uid,
                        write_date,
                        name,
                        alias_id,
                        description,
                        moderation,
                        moderation_notify,
                        moderation_notify_msg,
                        moderation_guidelines,
                        moderation_guidelines_msg,
                        access_mode,
                        access_group_id
                    )
             SELECT id,
                    active,
                    create_uid,
                    create_date,
                    write_uid,
                    write_date,
                    name,
                    alias_id,
                    description,
                    moderation,
                    moderation_notify,
                    {0},
                    moderation_guidelines,
                    {1},
                    CASE WHEN public = 'private'
                         THEN 'members'
                         ELSE public
                    END,
                    group_public_id
               FROM mail_channel
              WHERE email_send = TRUE
        """.format(
            util.pg_text2html("moderation_notify_msg"),
            util.pg_text2html("moderation_guidelines_msg"),
        ),
        [util.ref(cr, "base.group_user")],
    )

    # Set back FK on `mail_group_id` column of `mail_group_moderation` now that it is
    # created and populated
    cr.execute("ALTER TABLE mail_group_moderation DROP COLUMN mail_group_id")
    cr.execute("ALTER TABLE mail_group_moderation RENAME COLUMN _mail_group_id TO mail_group_id")
    cr.execute(
        """
        ALTER TABLE mail_group_moderation
            ALTER COLUMN mail_group_id SET NOT NULL,
            ADD CONSTRAINT mail_group_moderation_mail_group_id_fkey
               FOREIGN KEY (mail_group_id)
                REFERENCES mail_group(id)
                 ON DELETE CASCADE
        """
    )

    # 2. Update <mail.group.moderation> by normalizing the email column
    cr.execute("SELECT DISTINCT email FROM mail_group_moderation")
    emails = [result[0] for result in cr.fetchall()]
    emails = [(email_normalize(email), email) for email in emails]

    cr.executemany(
        """
        UPDATE mail_group_moderation
           SET email = %s
         WHERE email = %s
        """,
        emails,
    )

    # 3. Update the <mail.alias> linked to the <mail.group>
    cr.execute(
        """
        UPDATE mail_alias
           SET alias_model_id = %(model_mail_group)s,
               alias_parent_model_id = %(model_mail_group)s
          FROM mail_group AS mg
         WHERE alias_force_thread_id = mg.id
           AND alias_model_id = %(model_mail_channel)s
        """,
        {
            "model_mail_channel": env["ir.model"]._get("mail.channel").id,
            "model_mail_group": env["ir.model"]._get("mail.group").id,
        },
    )

    # 4. Add the member to the <mail.group>
    cr.execute(
        """
        INSERT INTO mail_group_member (
                        create_uid,
                        create_date,
                        write_uid,
                        write_date,
                        email,
                        partner_id,
                        mail_group_id
                    )
             SELECT mcp.create_uid,
                    mcp.create_date,
                    mcp.write_uid,
                    mcp.write_date,
                    p.email,
                    p.id,
                    mcp.channel_id
               FROM mail_channel_partner AS mcp
               JOIN mail_group AS mg
                 ON mg.id = mcp.channel_id
               JOIN res_partner AS p
                 ON p.id = mcp.partner_id
                AND p.active = TRUE
                 ON CONFLICT DO NOTHING
        """
    )

    # 5. Create the <mail.group.message> and move moderation fields
    cr.execute(
        """
        INSERT INTO mail_group_message (
                        create_uid,
                        create_date,
                        write_uid,
                        write_date,
                        mail_group_id,
                        mail_message_id,
                        moderation_status,
                        moderator_id
                    )
             SELECT mm.create_uid,
                    mm.create_date,
                    mm.write_uid,
                    mm.write_date,
                    mg.id,
                    mm.id,
                    COALESCE(mm.moderation_status, 'accepted'),
                    mm.moderator_id
               FROM mail_group as mg
               JOIN mail_message AS mm
                 ON mm.model = 'mail.channel'
                AND mm.message_type = 'email'
                AND mm.res_id = mg.id
        """
    )

    # 6. Move the moderators to the new table (moderator_ids fields on <mail.group>)
    cr.execute(
        """
        INSERT INTO mail_group_moderator_rel (
                        mail_group_id,
                        res_users_id
                    )
             SELECT mg.id,
                    mcmr.res_users_id
               FROM mail_channel_moderator_rel AS mcmr
               JOIN mail_group AS mg
                 ON mg.id = mcmr.mail_channel_id

        """
    )

    # 7. Move related records (e.g. attachments, messages) onto <mail.group>
    for ir in util.indirect_references(cr, bound_only=True):
        cr.execute(
            f"""
            UPDATE "{ir.table}" t
               SET {ir.model_filter(placeholder="'mail.group'")}
              FROM mail_group AS mg
             WHERE {ir.model_filter(prefix="t.", placeholder="'mail.channel'")}
               AND t.{ir.res_id} = mg.id
            """
        )

    # 8. Re-compute the field "group_message_parent_id" on <mail.group.message>
    cr.execute(
        """
        UPDATE mail_group_message AS group_child
           SET group_message_parent_id = group_parent.id
          FROM mail_group_message AS group_parent
          JOIN mail_message AS parent
            ON parent.id = group_parent.mail_message_id
          JOIN mail_message AS child
            ON child.parent_id = parent.id
         WHERE child.id = group_child.mail_message_id
        """
    )

    util.recompute_fields(cr, "mail.group.member", ["email_normalized"])
    util.recompute_fields(cr, "mail.group.message", ["email_from_normalized"])

    # Update the sequence of the ID column on "mail_group"
    cr.execute(
        """
        SELECT setval(
                'mail_group_id_seq',
                COALESCE((SELECT max(id) FROM mail_group), 1)
        )
        """
    )
    util.if_unchanged(cr, "mail_group.mail_template_guidelines", util.update_record_from_xml)
    util.if_unchanged(cr, "mail_group.mail_template_list_subscribe", util.update_record_from_xml)
    util.if_unchanged(cr, "mail_group.mail_template_list_unsubscribe", util.update_record_from_xml)
