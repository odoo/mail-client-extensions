# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Sponsor image. Was stored as `image_128`. In the now merged module `website_event_track_online` module,
    # image_512 is stored.
    cr.execute(
        """
        DELETE FROM ir_attachment a
              WHERE a.res_model = 'event.sponsor'
                AND a.res_field = 'image_128'
                AND EXISTS(
                  SELECT 1
                    FROM ir_attachment b
                   WHERE b.res_model = a.res_model
                     AND b.res_id = a.res_id
                     AND b.res_field = 'image_512'
                )
        """
    )
    cr.execute(
        """
        WITH same_as_partner AS (
        SELECT s.partner_id, a.id
          FROM event_sponsor s
          JOIN ir_attachment a ON a.res_id = s.id AND a.res_model = 'event.sponsor' AND a.res_field = 'image_128'
          JOIN ir_attachment b ON b.res_id = s.partner_id AND b.res_model = 'res.partner' AND b.res_field = 'image_128'
         WHERE a.checksum = b.checksum
        )
        UPDATE ir_attachment a
           SET res_field = 'image_512',
               db_datas = p.db_datas, store_fname = p.store_fname, mimetype = p.mimetype, checksum = p.checksum
          FROM same_as_partner s,
               ir_attachment p
         WHERE a.id = s.id
           AND p.res_id = s.partner_id
           AND p.res_model = 'res.partner'
           AND p.res_field = 'image_512'
    """
    )
    cr.execute(
        "UPDATE ir_attachment SET res_field = 'image_512' WHERE res_model = 'event.sponsor' AND res_field = 'image_128'"
    )
