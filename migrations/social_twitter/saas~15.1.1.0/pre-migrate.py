# -*- coding: utf-8 -*-


def migrate(cr, version):
    # remove duplicate tweets from the database
    cr.execute(
        """
        DELETE FROM social_stream_post WHERE id IN (
             SELECT unnest((array_agg(id ORDER BY id DESC))[2:])
               FROM social_stream_post
           GROUP BY (twitter_tweet_id, stream_id)
             HAVING count(*) > 1
        );
        """
    )
