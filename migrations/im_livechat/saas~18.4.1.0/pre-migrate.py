from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "im_livechat_channel", "max_sessions_mode"):
        util.create_column(cr, "im_livechat_channel", "block_assignment_during_call", "boolean")
        cr.execute("""
          UPDATE im_livechat_channel
             SET block_assignment_during_call = True
           WHERE max_sessions_mode = 'limited'
        """)
