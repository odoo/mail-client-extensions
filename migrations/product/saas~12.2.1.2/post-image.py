# -*- coding: utf-8 -*-
import logging
import os
import re

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.account.saas~12.3."
_logger = logging.getLogger(NS + __name__)


FORCE_COPY = re.split(r"[,\s]+", os.getenv("MIG_S122_FORCE_COPY_IMAGES_MODELS", ""))

SUFFIXES = ["big", "large", "medium", "small"]
if util.version_gte("saas~12.5"):
    SUFFIXES = ["1024", "512", "256", "128"]

CRON_CODE = """
# Make sure we process all images by ordering on `write_date`
# and forcing to update the `write_date` in case the image coudln't be resized
# because it was not in the filestore.
try:
    # 13.0 and upper
    add_to_compute = env.add_to_compute
except Exception:
    # before 13.0
    add_to_compute = env.add_todo

images_to_resize = model.search(
    [("index_content", "=", "image_is_not_yet_resized"), ("res_field", "!=", False)], limit=1000, order="write_date ASC"
)
images_recomputed = model.browse()
images_left = model.browse()
for image in images_to_resize:
    if image.with_context(bin_size=True).datas:
        res_model = env[image.res_model]
        add_to_compute(res_model._fields[image.res_field], res_model.browse(image.res_id))
        images_recomputed |= image
    else:
        images_left |= image
images_recomputed.recompute()
images_recomputed.write({"index_content": "image"})
images_left.write({"index_content": "image_is_not_yet_resized"})
"""


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


def image_mixin_recompute_fields(cr, model, infix="", suffixes=SUFFIXES, chunk_size=5000):
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

    def get_ids():
        # FIXME handle when attachments are stored in database
        with util.named_cursor(cr, 1000) as ncr:
            ncr.execute(
                """
                SELECT res_id, store_fname
                  FROM ir_attachment
                 WHERE res_model = %s
                   AND res_field = %s
                   AND res_id IS NOT NULL
                """,
                [model, orig_field],
            )
            chunk = ncr.fetchmany(chunk_size)
            while chunk:
                not_ids = []
                has_ids = []
                for res_id, store_fname in chunk:
                    if model not in FORCE_COPY and store_fname and os.path.isfile(full_path(store_fname)):
                        has_ids.append(res_id)
                    else:
                        not_ids.append(res_id)
                yield not_ids, has_ids
                chunk = ncr.fetchmany(chunk_size)

    cr.execute(
        """
        SELECT count(*)
          FROM ir_attachment
         WHERE res_model = %s
           AND res_field = %s
           AND res_id IS NOT NULL
        """,
        [model, orig_field],
    )
    size = (cr.fetchone()[0] - 1) // chunk_size + 1
    inject_cron = False
    for not_ids, has_ids in util.log_progress(get_ids(), _logger, "chunks of {} records".format(chunk_size), size):
        if has_ids:
            compute_fields = list(fields)
            if zoom:
                compute_fields += [zoom]
            for record_id in has_ids:
                try:
                    util.recompute_fields(cr, model, compute_fields, ids=[record_id])
                except Exception:
                    # If the image is broken, fuck it
                    _logger.exception("Cannot resize images, %s.%s,%s", model, compute_fields, record_id)
                    not_ids.append(record_id)

        if not_ids:
            cols = ", ".join(util.get_columns(cr, "ir_attachment", ignore=("id", "res_field", "index_content")))
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
                [fields, model, orig_field, not_ids],
            )
            if zoom:
                table = util.table_of_model(cr, model)
                cr.execute("UPDATE {} SET {}=false WHERE id = ANY(%s)".format(table, zoom), [not_ids])
            inject_cron = True

    if inject_cron:
        # Inject the cron which will resize the images which have not been resized during the upgrade
        util.create_cron(cr, "Resize Images", "ir.attachment", CRON_CODE)


def migrate(cr, version):
    # `image_medium` and `image_small` were already there...
    image_mixin_recompute_fields(cr, "product.template", suffixes=SUFFIXES[:2])
    infix = "_raw" if not util.version_gte("saas~12.5") else "_variant"
    image_mixin_recompute_fields(cr, "product.product", infix=infix)
