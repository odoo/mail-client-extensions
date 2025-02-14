from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "l10n_br_edi.mail_template_move_update", util.update_record_from_xml)
