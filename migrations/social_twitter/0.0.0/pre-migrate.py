from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # remove twitter_likes streams from the database, posts linked to them should be automatically
    # removed via the ondelete=cascade
    if util.version_gte("15.0"):
        cr.execute(
            """
                DELETE FROM social_stream to_remove
                      USING social_stream ss
                       JOIN social_stream_type sst
                         ON ss.stream_type_id = sst.id
                  LEFT JOIN social_account sa
                         ON ss.twitter_followed_account_id = sa.id
                  LEFT JOIN social_twitter_account sta
                         ON sa.twitter_user_id = sta.twitter_id
                      WHERE to_remove.id = ss.id
                        AND sst.stream_type = 'twitter_likes'
                        AND sta IS NULL
                """
        )
