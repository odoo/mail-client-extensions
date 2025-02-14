from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "gamification.mail_template_data_new_rank_reached", util.update_record_from_xml)
