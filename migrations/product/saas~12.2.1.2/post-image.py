# -*- coding: utf-8 -*-
import logging
import os
import re

from odoo import tools

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.account.saas~12.3."
_logger = logging.getLogger(NS + __name__)


FORCE_COPY = re.split(r"[,\s]+", os.getenv("MIG_S122_FORCE_COPY_IMAGES_MODELS", ""))

SUFFIXES = ["big", "large", "medium", "small"]
if util.version_gte("saas~12.5"):
    SUFFIXES = ["1024", "512", "256", "128"]


def check_field(cr, model, fieldname):
    cr.execute("SELECT id FROM ir_model_fields WHERE model=%s AND name=%s", [model, fieldname])
    return bool(cr.rowcount)


def get_orig_field(cr, model, infix):
    for field in [
        "image{}_1920".format(infix),
        "image{}_original".format(infix),
        "image",
    ]:
        if check_field(cr, model, field):
            return field
    return False


def image_mixin_recompute_fields(cr, model, infix="", suffixes=SUFFIXES, chunk_size=500):
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

    not_ids = []
    has_ids = []
    for res_id, store_fname in cr.fetchall():
        if model not in FORCE_COPY and store_fname and os.path.isfile(full_path(store_fname)):
            has_ids.append(res_id)
        else:
            not_ids.append(res_id)

    if has_ids:
        compute_fields = list(fields)
        if zoom:
            compute_fields += [zoom]
        for record_id in util.log_progress(has_ids, _logger, qualifier="records"):
            try:
                util.recompute_fields(cr, model, compute_fields, ids=[record_id])
            except Exception:
                # If the image is broken, fuck it
                _logger.exception("Cannot resize images, %s.%s,%s", model, compute_fields, record_id)
                not_ids.append(record_id)

    if not_ids:
        cols = ", ".join(util.get_columns(cr, "ir_attachment", ignore=("id", "res_field", "index_content"))[0])
        size = (len(not_ids) + chunk_size - 1) / chunk_size
        qual = "%s %d-bucket" % (model, chunk_size)
        for sub_ids in util.log_progress(util.chunks(not_ids, chunk_size, list), _logger, qualifier=qual, size=size):
            cr.execute(
                """
                INSERT INTO ir_attachment(res_field, {cols}, index_content)
                     SELECT unnest(%s), {cols}, 'image_is_not_yet_resized'
                       FROM ir_attachment
                      WHERE res_model = %s
                        AND res_field = %s
                        AND res_id IS NOT NULL
                        AND res_id = ANY(%s)
            """.format(
                    cols=cols
                ),
                [fields, model, orig_field, sub_ids],
            )
        if zoom:
            table = util.table_of_model(cr, model)
            qual = "%s:%s %d-bucket" % (model, zoom, chunk_size)
            chnk = util.chunks(not_ids, chunk_size, list)
            for sub_ids in util.log_progress(chnk, _logger, qualifier=qual, size=size):
                cr.execute("UPDATE {} SET {}=false WHERE id = ANY(%s)".format(table, zoom), [sub_ids])

        # Inject the cron which will resize the images which have not been resized during the upgrade
        if not util.ref(cr, "__upgrade__.post_upgrade_resize_image"):
            cron_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resize-images-cron.xml")
            with open(cron_file, "rb") as fp:
                tools.convert_xml_import(cr, "__upgrade__", fp, {})


def migrate(cr, version):
    # `image_medium` and `image_small` were already there...
    image_mixin_recompute_fields(cr, "product.template", suffixes=SUFFIXES[:2])
    infix = "_raw" if not util.version_gte("saas~12.5") else "_variant"
    image_mixin_recompute_fields(cr, "product.product", infix=infix)
