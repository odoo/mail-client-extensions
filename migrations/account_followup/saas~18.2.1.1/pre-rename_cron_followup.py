from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, *util.expand_braces("account_followup.ir_cron_{auto_post_draft_entry,follow_up}"), on_collision="merge"
    )
