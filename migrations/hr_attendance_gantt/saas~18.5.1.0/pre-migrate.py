from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, 'hr_attendance_gantt.action_open_gantt_create_view_form')
