# -*- coding: utf-8 -*-
import re


def migrate(cr, version):
    changes = [
        ("acquirer_id", "provider_id"),
        ("tx.provider", "tx.provider_code"),
        ("token_id.name", "token_id.display_name"),
    ]
    for old, new in changes:
        re_old = rf"\y{re.escape(old)}\y"
        match = f'exists($.* ? (@ like_regex "{re_old}"))'
        cr.execute(
            """
WITH upd AS (
     SELECT t.id,
            jsonb_object_agg(v.key, regexp_replace(v.value, %s, %s, 'g')) AS body_html
       FROM mail_template t
       JOIN LATERAL jsonb_each_text(t.body_html) v
         ON true
      WHERE t.model = 'sale.order'
        AND jsonb_path_match(t.body_html, %s)
      GROUP BY t.id
)
UPDATE mail_template orig
   SET body_html = upd.body_html
  FROM upd
 WHERE upd.id=orig.id
""",
            [re_old, new, match],
        )
