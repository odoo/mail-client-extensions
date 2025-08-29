from odoo.upgrade import util


def migrate(cr, version):
    act_id = util.ref(cr, "mail.mail_activity_data_todo")
    if act_id is not None:
        cr.execute(
            """
            WITH info AS (
                SELECT id,
                       res_model
                  FROM mail_activity_type
                 WHERE id = %s
                   AND res_model IS NOT NULL
            ) UPDATE mail_activity_type at
                 SET res_model = NULL
                FROM info
               WHERE at.id = info.id
           RETURNING info.res_model
            """,
            [act_id],
        )

        if cr.rowcount:
            model_name = cr.fetchone()[0]

            activity_link = util.get_anchor_link_to_record(
                "mail.activity.type", act_id, "<pre>mail.mail_activity_data_todo</pre>"
            )

            util.add_to_migration_reports(
                category="Mail",
                message=f"""
                The standard record {activity_link} was restricted to the model {model_name!r}
                and it has been reset to no model. In Odoo 17 <pre>mail.mail_activity_data_todo</pre>
                is shared for all Mail Activity Plan Templates thus it cannot be restricted to any specific model.
                """,
                format="html",
            )
