# -*- coding: utf-8 -*-
import os
from odoo.addons.base.maintenance.migrations import util


SUFFIXES = ["big", "large", "medium", "small"]
if util.version_gte("saas~12.5"):
    SUFFIXES = ["1024", "256", "128"]


def check_field(cr, model, fieldname):
    cr.execute("SELECT id FROM ir_model_fields WHERE model=%s AND name=%s", [model, fieldname])
    return bool(cr.rowcount)


def get_orig_field(cr, model, infix):
    for field in ["image{}_1920".format(infix), "image_1920", "image{}_original".format(infix), "image_original", "image"]:
        if check_field(cr, model, field):
            return field
    return False


def check_field(cr, model, fieldname):
    cr.execute("SELECT id FROM ir_model_fields WHERE model=%s AND name=%s", [model, fieldname])
    return bool(cr.rowcount)


def image_mixin_recompute_fields(cr, model, infix="", suffixes=SUFFIXES):
    fields = ["image{}_{}".format(infix, s) for s in SUFFIXES]
    fields = [f for f in fields if check_field(cr, model, f)]

    if not fields:
        return

    zoom = "can_image{}_be_zoomed".format(infix)
    if not check_field(cr, model, zoom):
        zoom = None

    orig_field = get_orig_field(cr, model, infix)

    env = util.env(cr)
    full_path = env["ir.attachment"]._full_path

    # FIXME handle when attachments are stored in database
    cr.execute(
        """
        SELECT res_id, store_fname
          FROM ir_attachment
         WHERE res_model = %s
           AND res_field = %s
           AND res_id IS NOT NULL
    """,
        [model, orig_field],
    )

    all_ids = []
    has_ids = []
    for res_id, store_fname in cr.fetchall():
        all_ids.append(res_id)
        if os.path.isfile(full_path(store_fname)):
            has_ids.append(res_id)

    if len(all_ids) != len(has_ids):
        cols = ", ".join(util.get_columns(cr, "ir_attachment", ignore=("id", "res_field"))[0])
        cr.execute(
            """
            INSERT INTO ir_attachment(res_field, {cols})
                 SELECT unnest(%s), {cols}
                   FROM ir_attachment
                  WHERE res_model = %s
                    AND res_field = %s
                    AND res_id IS NOT NULL
                    AND res_id != ALL(%s)
        """.format(
                cols=cols
            ),
            [fields, model, orig_field, has_ids],
        )
        if zoom:
            table = util.table_of_model(cr, model)
            cr.execute("UPDATE {} SET {}=false WHERE id = ANY(%s)".format(table, zoom), [all_ids])

    if has_ids:
        if zoom:
            fields += [zoom]
        util.recompute_fields(cr, model, fields, has_ids)


def migrate(cr, version):
    # `image_medium` and `image_small` were already there...
    image_mixin_recompute_fields(cr, "product.template", suffixes=SUFFIXES[:2])
    image_mixin_recompute_fields(cr, "product.product", infix="_raw" if not util.version_gte("saas~12.5") else "_variant")
