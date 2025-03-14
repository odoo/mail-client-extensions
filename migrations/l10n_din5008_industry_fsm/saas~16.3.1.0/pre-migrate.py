from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "l10n_din5008_document_title")
