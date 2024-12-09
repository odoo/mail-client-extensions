from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_es.mainland_es", force_create=False, fields=["code"])
