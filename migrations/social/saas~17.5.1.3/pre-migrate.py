from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "social.post.template", "message_length")

    modules = [
        "social_facebook",
        "social_twitter",
        "social_linkedin",
        "social_instagram",
    ]
    for module in modules:
        if not util.module_installed(cr, module):
            continue

        media = module[len("social_") :]
        for table, m2m_prefix in [
            ("social_post", ""),
            ("social_post_template", "template_"),
        ]:
            new_m2m_table = f"{m2m_prefix}{media}_image_ids_rel"
            m2m_table = f"ir_attachment_{table}_rel"
            rel_field = f"{table}_id"
            util.create_column(cr, table, f"{media}_message", "text")
            query = util.format_query(cr, "UPDATE {} SET {} = message", table, f"{media}_message")
            cr.execute(query)

            util.create_m2m(cr, new_m2m_table, table, "ir_attachment")
            query = util.format_query(
                cr,
                """
               INSERT INTO {}({}, ir_attachment_id)
                    SELECT {}, ir_attachment_id
                      FROM {}
                    """,
                new_m2m_table,
                rel_field,
                rel_field,
                m2m_table,
            )
            cr.execute(query)
