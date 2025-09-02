from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~18.2"):
        _ensure_uoms(cr)


def _ensure_uoms(cr):
    for category, uom in [
        ("uom.product_uom_categ_unit", "uom.product_uom_unit"),
        ("uom.product_uom_categ_kgm", "uom.product_uom_kgm"),
        ("uom.uom_categ_wtime", "uom.product_uom_day"),
        ("uom.uom_categ_length", "uom.product_uom_meter"),
        ("uom.product_uom_categ_vol", "uom.product_uom_litre"),
    ]:
        unit_category_id = util.ref(cr, category)
        if unit_category_id and not util.ref(cr, uom):
            util.ensure_xmlid_match_record(
                cr,
                uom,
                "uom.uom",
                {
                    "uom_type": "reference",
                    "category_id": unit_category_id,
                },
            )
