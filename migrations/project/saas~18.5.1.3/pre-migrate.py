from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "project.action_server_view_my_task")
