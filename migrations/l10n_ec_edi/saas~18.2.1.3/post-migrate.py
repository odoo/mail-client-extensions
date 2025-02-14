from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "l10n_ec_edi.email_template_edi_withhold", util.update_record_from_xml)
