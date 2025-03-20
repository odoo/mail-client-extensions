from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides_forum.website_slides_forum_header")

    # Populating new Image field with cloned values from related courses.
    columns = util.get_columns(cr, "ir_attachment", ignore=("id", "res_id", "res_model"))
    query = util.format_query(
        cr,
        """
       INSERT INTO ir_attachment (res_id, res_model, {insert_cols})
            SELECT f.id AS res_id, 'forum.forum' AS res_model, {select_cols}
              FROM ir_attachment AS att
              JOIN slide_channel AS sc
                ON att.res_id = sc.id
               AND att.res_model = 'slide.channel'
               AND att.res_field ~ '^image_[[:digit:]]+$'
              JOIN forum_forum f
                ON sc.id = f.slide_channel_id
                -- skip cloning if already existing
         LEFT JOIN ir_attachment forum_att
                ON forum_att.res_id = f.id
               AND forum_att.res_model = 'forum.forum'
               AND forum_att.res_field = att.res_field
             WHERE forum_att.id IS NULL
        """,
        insert_cols=columns,
        select_cols=columns.using(alias="att"),
    )
    cr.execute(query)
