# -*- coding: utf-8 -*-

header_templates = [
    "website.template_header_hamburger",
    "website.template_header_vertical",
    "website.template_header_sidebar",
    "website.template_header_slogan",
    "website.template_header_contact",
    "website.template_header_boxed",
    "website.template_header_centered_logo",
    "website.template_header_image",
    "website.template_header_hamburger_full",
    "website.template_header_magazine",
    "website.template_header_default",
]


def migrate(cr, version):
    cr.execute(
        # dsaht = Duplicated Specific Active Header Template
        """
          WITH dsaht AS (
              SELECT unnest((array_agg(id ORDER BY COALESCE(write_date, create_date) ASC, id))[2:]) as id
                FROM ir_ui_view
               WHERE website_id IS NOT NULL
                 AND active = true
                 AND key IN %(header_keys)s
            GROUP BY website_id
              HAVING count(id) > 1
             )
        UPDATE ir_ui_view v
           SET active = false
          FROM dsaht
         WHERE v.id = dsaht.id
    """,
        {"header_keys": tuple(header_templates)},
    )
