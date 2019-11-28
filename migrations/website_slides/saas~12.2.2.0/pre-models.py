# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    # channel
    util.rename_field(cr, "slide.channel", *eb("description{,_html}"))
    util.rename_field(cr, "slide.channel", *eb("nbr_presentation{s,}"))
    util.rename_field(cr, "slide.channel", *eb("nbr_document{s,}"))
    util.rename_field(cr, "slide.channel", *eb("nbr_video{s,}"))
    util.rename_field(cr, "slide.channel", *eb("nbr_infographic{s,}"))
    util.rename_field(cr, "slide.channel", *eb("total{,_slides}"))
    util.rename_field(cr, "slide.channel", "group_ids", "enroll_group_ids")

    util.create_column(cr, "slide_channel", "description", "text")
    util.create_column(cr, "slide_channel", "channel_type", "varchar")
    util.create_column(cr, "slide_channel", "user_id", "int4")
    util.create_column(cr, "slide_channel", "slide_last_update", "date")
    util.create_column(cr, "slide_channel", "access_token", "varchar")
    util.create_column(cr, "slide_channel", "nbr_webpage", "int4")
    util.create_column(cr, "slide_channel", "nbr_quizz", "int4")
    util.create_column(cr, "slide_channel", "total_views", "int4")
    util.create_column(cr, "slide_channel", "total_votes", "int4")
    util.create_column(cr, "slide_channel", "total_time", "float8")
    util.create_column(cr, "slide_channel", "allow_comment", "boolean")
    util.create_column(cr, "slide_channel", "enroll", "varchar")
    util.create_column(cr, "slide_channel", "enroll_msg", "text")

    util.create_column(cr, "slide_channel", "karma_gen_slide_vote", "int4")
    util.create_column(cr, "slide_channel", "karma_gen_channel_rank", "int4")
    util.create_column(cr, "slide_channel", "karma_gen_channel_finish", "int4")
    util.create_column(cr, "slide_channel", "karma_review", "int4")
    util.create_column(cr, "slide_channel", "karma_slide_comment", "int4")
    util.create_column(cr, "slide_channel", "karma_slide_vote", "int4")

    util.remove_field(cr, "slide.channel", "custom_slide_id")
    util.remove_field(cr, "slide.channel", "promoted_slide_id")
    util.remove_field(cr, "slide.channel", "can_see")
    util.remove_field(cr, "slide.channel", "can_see_full")

    cr.execute(
        """
        UPDATE slide_channel
           SET channel_type = 'documentation',
               access_token = md5(concat(clock_timestamp()::varchar, ';', random()::varchar))::uuid::varchar,
               nbr_webpage = 0,
               nbr_quizz = 0,
               total_votes = 0,
               total_time = 0,
               allow_comment = TRUE,
               enroll = 'public'
    """
    )

    cr.execute(
        """
        WITH chan_upd AS (
           SELECT channel_id, max(greatest(create_date, write_date))::date AS upd
             FROM slide_slide
         GROUP BY channel_id
        )
        UPDATE slide_channel c
           SET slide_last_update = u.upd
          FROM chan_upd u
         WHERE c.id = u.channel_id
    """
    )
    cr.execute("UPDATE slide_channel SET promote_strategy = 'latest' WHERE promote_strategy IN ('none', 'custom')")
    cr.execute("UPDATE slide_channel SET visibility = 'members' WHERE visibility IN ('private', 'partial')")

    cr.execute("ALTER TABLE rel_channel_groups RENAME TO res_groups_slide_channel_rel")
    cr.execute("ALTER TABLE res_groups_slide_channel_rel RENAME COLUMN channel_id TO slide_channel_id")
    cr.execute("ALTER TABLE res_groups_slide_channel_rel RENAME COLUMN group_id TO res_groups_id")

    # channel.partner
    cr.execute(
        """
        CREATE TABLE slide_channel_partner(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            channel_id int4,
            partner_id int4,
            completed boolean,
            completion int4
        )
    """
    )
    cr.execute(
        """
        INSERT INTO slide_channel_partner (channel_id, partner_id, completed, completion)
             SELECT r.slide_channel_id, u.partner_id, FALSE, 0
               FROM res_groups_slide_channel_rel r
               JOIN res_groups_users_rel s ON (s.gid = r.res_groups_id)
               JOIN res_users u ON (u.id = s.uid)
    """
    )

    # category
    util.rename_field(cr, "slide.category", *eb("nbr_presentation{s,}"))
    util.rename_field(cr, "slide.category", *eb("nbr_document{s,}"))
    util.rename_field(cr, "slide.category", *eb("nbr_video{s,}"))
    util.rename_field(cr, "slide.category", *eb("nbr_infographic{s,}"))
    util.rename_field(cr, "slide.category", *eb("total{,_slides}"))

    util.create_column(cr, "slide_category", "nbr_webpage", "int4")
    util.create_column(cr, "slide_category", "nbr_quizz", "int4")

    # slide
    cr.execute("ALTER TABLE slide_slide DROP CONSTRAINT IF EXISTS slide_slide_name_uniq")
    util.rename_field(cr, "slide.slide", "image", "image_original")
    util.rename_field(cr, "slide.slide", "image_medium", "image_medium")
    util.rename_field(cr, "slide.slide", "image_thumb", "image_small")
    util.rename_field(cr, "slide.slide", "embed_views", "public_views")  # not really the same field

    util.create_column(cr, "slide_slide", "can_image_be_zoomed", "boolean")

    util.remove_field(cr, "slide.slide", "download_security")

    util.create_column(cr, "slide_slide", "sequence", "int4")
    util.create_column(cr, "slide_slide", "category_sequence", "int4")
    util.create_column(cr, "slide_slide", "user_id", "int4")
    util.create_column(cr, "slide_slide", "access_token", "varchar")
    util.create_column(cr, "slide_slide", "is_preview", "boolean")
    util.create_column(cr, "slide_slide", "completion_time", "float8")
    for attemp in {"first", "second", "third", "fourth"}:
        util.create_column(cr, "slide_slide", "quiz_%s_attempt_reward" % attemp, "int4")
    util.create_column(cr, "slide_slide", "html_content", "text")

    cr.execute(
        """
        UPDATE slide_slide
           SET public_views = 0,    -- reset
               sequence = id,
               user_id = create_uid,
               access_token = md5(concat(clock_timestamp()::varchar, ';', random()::varchar))::uuid::varchar,
               is_preview = FALSE,
               completion_time = 1,
               quiz_first_attempt_reward = 10,
               quiz_second_attempt_reward = 7,
               quiz_third_attempt_reward = 5,
               quiz_fourth_attempt_reward = 2
    """
    )
    cr.execute(
        """
        UPDATE slide_slide s
           SET category_sequence = c.sequence
          FROM slide_category c
         WHERE c.id = s.category_id
    """
    )
