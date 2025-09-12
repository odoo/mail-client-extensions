from markupsafe import Markup

from odoo.upgrade import util


def migrate(cr, version):
    # Recompute the stored computed fields that might have changed of the modified and newly created
    # sale orders.
    query = """
        SELECT id
          FROM sale_order
         WHERE _upg_rental_parent_so_id IS NOT NULL
         UNION ALL
        SELECT _upg_rental_parent_so_id
          FROM sale_order
         WHERE _upg_rental_parent_so_id IS NOT NULL
      GROUP BY _upg_rental_parent_so_id
        """
    fields_to_recompute = [
        # sale
        "amount_untaxed",
        "amount_tax",
        "amount_total",
        "amount_to_invoice",
        # sale_renting
        "is_rental_order",
        "rental_status",
        "next_action_date",
    ]
    if util.module_installed(cr, "sale_stock"):
        fields_to_recompute += ["effective_date"]
    if util.module_installed(cr, "sale_margin"):
        fields_to_recompute += ["margin", "margin_percent"]
    util.recompute_fields(cr, "sale.order", fields=fields_to_recompute, query=query)

    # add a message on new SO with a link to the original
    cr.execute(
        """
           SELECT so.id, old_so.id, old_so.name
             FROM sale_order so
             JOIN sale_order old_so
               ON old_so.id = so._upg_rental_parent_so_id
            WHERE so._upg_rental_parent_so_id IS NOT NULL
        """
    )

    values = {new_so_id: (old_so_id, old_so_name) for (new_so_id, old_so_id, old_so_name) in cr.fetchall()}

    for so in util.iter_browse(util.env(cr)["sale.order"], values.keys()):
        so.message_post(
            body=Markup(
                "This SO has been split from <a href=# data-oe-model='sale.order' data-oe-id='{so[0]:d}'>{so[1]}</a> based on the rental period."
            ).format(so=values[so.id])
        )

    cr.execute(
        """
        -- copy the followers and their type from the orignal so to the copy
        with followers_tab AS (
            SELECT so.id AS res_id,
                   mf.partner_id AS partner_id,
                   mf.res_model AS res_model,
                   mf.id AS mail_followers_id
              FROM mail_followers AS mf
        INNER JOIN sale_order AS so
                ON so._upg_rental_parent_so_id = mf.res_id
             WHERE mf.res_model='sale.order'
               AND so._upg_rental_parent_so_id IS NOT NULL
        ),
        new_ids AS (
            INSERT INTO mail_followers(res_id, partner_id, res_model)
                 SELECT res_id, partner_id, res_model
                   FROM followers_tab
              RETURNING id, res_id, partner_id
        )
        INSERT INTO mail_followers_mail_message_subtype_rel(mail_followers_id, mail_message_subtype_id)
             SELECT new_ids.id, subtype.mail_message_subtype_id
               FROM mail_followers_mail_message_subtype_rel as subtype
         INNER JOIN followers_tab
                 ON followers_tab.mail_followers_id = subtype.mail_followers_id
         INNER JOIN new_ids
                 ON new_ids.res_id = followers_tab.res_id
              WHERE new_ids.partner_id = followers_tab.partner_id
        """
    )

    cr.execute(
        """
        -- copy the tags from the original so to the copy
         INSERT INTO sale_order_tag_rel(order_id, tag_id)
              SELECT so.id, tag.tag_id
                FROM sale_order so
                JOIN sale_order old_so
                  ON old_so.id = so._upg_rental_parent_so_id
          INNER JOIN sale_order_tag_rel AS tag
                  ON tag.order_id = old_so.id
               WHERE so._upg_rental_parent_so_id IS NOT NULL
        """
    )

    util.remove_column(cr, "sale_order", "_upg_rental_parent_so_id")
    util.remove_column(cr, "sale_order", "_upg_rental_linked_sol_ids")
