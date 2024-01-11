from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "social_stream_post", "facebook_reactions_count", "varchar")

    cr.execute(
        """
         UPDATE social_stream_post
            SET facebook_reactions_count='{"LIKE": ' || facebook_likes_count || ' }'
          WHERE facebook_likes_count > 0;
        """
    )
