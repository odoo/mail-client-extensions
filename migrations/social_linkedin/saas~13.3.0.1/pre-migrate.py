# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # remove all personal LinkedIn accounts
    cr.execute(
        """
        DELETE FROM social_account
              USING social_media
              WHERE linkedin_account_id like '%person%';
    """
    )

    # update media (now LinkedIn can have stream)
    cr.execute(
        """
             UPDATE social_media
                SET has_streams=true
              WHERE media_type = 'linkedin';
    """
    )

    # update social accounts (now LinkedIn accounts support stats and trends)
    cr.execute(
        """
             UPDATE social_account
                SET has_trends=true, has_account_stats=true
               FROM social_media
              WHERE social_account.media_id = social_media.id
                AND social_media.media_type = 'linkedin';
    """
    )

    util.rename_field(cr, "social_account", "linkedin_account_id", "linkedin_account_urn")

    # add new fields
    util.create_column(cr, "social_stream_post", "linkedin_post_urn", "varchar")
    util.create_column(cr, "social_stream_post", "linkedin_author_urn", "varchar")
    util.create_column(cr, "social_stream_post", "linkedin_author_vanity_name", "varchar")
    util.create_column(cr, "social_stream_post", "linkedin_author_image_url", "varchar")
    util.create_column(cr, "social_stream_post", "linkedin_comments_count", "integer")
    util.create_column(cr, "social_stream_post", "linkedin_likes_count", "integer")
