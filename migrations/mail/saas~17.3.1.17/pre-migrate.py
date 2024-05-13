from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "discuss_channel_member", "new_message_separator", "integer", default=0)
    query = """
        UPDATE discuss_channel_member
           SET new_message_separator = seen_message_id
         WHERE seen_message_id IS NOT NULL

    """
    util.explode_execute(cr, query, table="discuss_channel_member")
