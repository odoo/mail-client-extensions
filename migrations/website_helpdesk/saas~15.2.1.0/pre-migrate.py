# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_helpdesk.website_helpdesk_form_team")
    util.remove_view(cr, "website_helpdesk.not_published_any_team")

    util.remove_record(cr, "website_helpdesk.website_menu_helpdesk")

    util.create_column(cr, "helpdesk_team", "website_menu_id", "int4")
    util.create_column(cr, "helpdesk_team", "website_id", "int4")
    util.create_column(cr, "helpdesk_team", "website_form_view_id", "int4")

    cr.execute(
        """
            UPDATE helpdesk_team AS t
               SET website_id = c.website_id
              FROM res_company AS c
             WHERE t.company_id = c.id
        """
    )

    cr.execute(
        """
          WITH ht_menu AS (
            INSERT INTO website_menu(name, url, parent_id, sequence, website_id)
                 SELECT t.name, CONCAT('/helpdesk/', t.id), m.id, 50, m.website_id
                   FROM helpdesk_team t
                   JOIN website_menu m ON m.website_id = t.website_id
                  WHERE m.parent_id IS NULL
                    AND t.use_website_helpdesk_form = true
                    AND t.is_published = true
              RETURNING id, substr(url, 11)::integer AS team_id
          )
            UPDATE helpdesk_team t
               SET website_menu_id = m.id
              FROM ht_menu m
             WHERE m.team_id = t.id
        """
    )
