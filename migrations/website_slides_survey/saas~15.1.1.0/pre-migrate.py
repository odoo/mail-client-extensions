from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_slides_survey.survey_survey_action_slides_report")
    util.remove_menus(cr, [util.ref(cr, "website_slides_survey.website_slides_menu_report_certification")])
    util.remove_constraint(cr, "slide_slide", "slide_slide_check_survey_id")
