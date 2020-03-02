# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "survey_survey", "certification_report_layout", "varchar")
    cr.execute("UPDATE survey_survey SET certification_report_layout = 'modern_purple'")

    util.force_noupdate(cr, "survey.certification_report_view", False)

    renames = util.splitlines("""
        {403,survey_403_page}
        {sfinished,survey_closed_finished}
        {retake_survey_button,survey_button_retake}
        survey_{,closed_}expired
        {,survey_}auth_required
        survey_void{,_content}
        {back,survey_button_form_view}

        survey_{init,page_start}
        survey{,_page_main}
        {page,survey_page_content}
        survey_{,page_main_}header
        question{,_container}

        {,question_}free_text
        {,question_}textbox
        {,question_}numerical_box
        {,question_}date
        {,question_}datetime
        {,question_}simple_choice
        {,question_}multiple_choice
        {,question_}matrix

        survey_{,page_}print

        {result,survey_page_statistics}
        {,question_}result_text
        {,question_}result_comments
        {,question_}result_choice
        {,question_}result_matrix
        {,question_}result_number
        {,question_}pagination
    """)

    for rename in renames:
        util.rename_xmlid(cr, *eb(f"survey.{rename}"), noupdate=False)
