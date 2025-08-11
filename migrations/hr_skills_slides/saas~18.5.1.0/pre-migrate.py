from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "hr_skills_slides.resume_type_training")
    util.remove_view(cr, "hr_skills_slides.resume_slides_line_view_form")
    util.remove_view(cr, "hr_skills_slides.user_preference_resume_view_form_inherit")

    cr.execute(
        """
        UPDATE hr_resume_line
           SET duration = slide_channel.total_time,
               course_type = 'elearning'
          FROM slide_channel
         WHERE slide_channel.id = hr_resume_line.channel_id
        """
    )
