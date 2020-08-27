# -*- coding: utf-8 -*-


def migrate(cr, version):
    # remove inconsistent social streams from the database
    cr.execute(
        """
        DELETE FROM social_stream s
              USING social_stream_type t
              WHERE s.twitter_followed_account_id IS NULL
                AND t.stream_type IN ('twitter_follow', 'twitter_likes')
                AND t.id = s.stream_type_id
        """
    )
