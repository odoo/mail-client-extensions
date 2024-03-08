from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_model(cr, "homework.location.wizard", "hr_homeworking", "hr_homeworking_calendar")

    util.rename_xmlid(cr, *eb("hr_homeworking{,_calendar}.homeworking_location_wizard_own_rule"))
    util.rename_xmlid(cr, *eb("hr_homeworking{,_calendar}.homeworking_location_wizard_admin_rule"))
    util.rename_xmlid(cr, *eb("hr_homeworking{,_calendar}.access_homework_location_wizard"))
    util.rename_xmlid(cr, *eb("hr_homeworking{,_calendar}.homework_location_wizard_view_form"))
    util.rename_xmlid(cr, *eb("hr_homeworking{,_calendar}.set_location_wizard_action"))
