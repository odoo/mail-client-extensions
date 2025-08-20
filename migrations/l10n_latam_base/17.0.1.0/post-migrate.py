from odoo.upgrade import util


def migrate(cr, version):
    if util.ENVIRON.get("latam_base_create_column"):
        it_vat = util.ref(cr, "l10n_latam_base.it_vat")
        query = cr.mogrify("UPDATE res_partner SET l10n_latam_identification_type_id = %s", [it_vat]).decode()
        util.explode_execute(cr, query, table="res_partner")
