from odoo.upgrade import util


def migrate(cr, version):
    util.ENVIRON["latam_base_create_column"] = util.create_column(
        cr, "res_partner", "l10n_latam_identification_type_id", "int4"
    )
