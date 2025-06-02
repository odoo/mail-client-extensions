from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.sign_item_role_view_tree")
    util.remove_model(cr, "sign.duplicate.template.pdf")
    util.remove_model(cr, "sign.request.download")
    util.create_column(cr, "sign_request", "completion_date", "timestamp")
    util.explode_execute(
        cr,
        """
        WITH latest_request_items AS (
                SELECT sign_request_id, MAX(signing_date) AS max_signing_date
                  FROM sign_request_item
              GROUP BY sign_request_id
        )
        UPDATE sign_request sr
           SET completion_date = CASE
          WHEN sr.nb_wait > 0 THEN NULL
          ELSE latest_request_items.max_signing_date
           END
          FROM latest_request_items
         WHERE sr.id = latest_request_items.sign_request_id
        """,
        table="sign_request",
        alias="sr",
    )
