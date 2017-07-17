# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def convert(cr, model, field, encoded=True):
    table = util.table_of_model(cr, model)
    if not util.column_exists(cr, table, field):
        return
    env = util.env(cr)
    att_name = '%s(%%s).%s' % (model.title().replace('.', ''), field)
    A = env['ir.attachment']
    cr.execute("SELECT id, {field} FROM {table} WHERE {field} IS NOT NULL".format(**locals()))
    for rid, data in cr.fetchall():
        # we can't save create the attachment with res_model & res_id as it will fail computing
        # `res_name` field for non-loaded models. Store it naked and change it via SQL after.
        data = str(data)
        if not encoded:
            data = data.encode('base64')
        att = A.create({
            'name': att_name % rid,
            'datas': data,
            'type': 'binary',
        })
        cr.execute("""UPDATE ir_attachment
                         SET res_model=%s, res_id=%s, res_field=%s
                       WHERE id=%s
                   """, [model, rid, field, att.id])

    # free PG space
    util.remove_column(cr, table, field)

def migrate(cr, version):

    convert(cr, 'ir.ui.menu', 'web_icon_data')
    convert(cr, 'res.country', 'image')
    convert(cr, 'res.partner', 'image')
    convert(cr, 'res.partner', 'image_medium')
    convert(cr, 'res.partner', 'image_small')

    # process also other modules here (1 place to fix)
    convert(cr, 'fleet.vehicle.model.brand', 'image')
    convert(cr, 'fleet.vehicle.model.brand', 'image_medium')
    convert(cr, 'fleet.vehicle.model.brand', 'image_small')

    convert(cr, 'gamification.badge', 'image')

    convert(cr, 'hr.employee', 'image')
    convert(cr, 'hr.employee', 'image_medium')
    convert(cr, 'hr.employee', 'image_small')

    convert(cr, 'im_livechat.channel', 'image')
    convert(cr, 'im_livechat.channel', 'image_medium')
    convert(cr, 'im_livechat.channel', 'image_small')

    convert(cr, 'mail.channel', 'image')
    convert(cr, 'mail.channel', 'image_medium')
    convert(cr, 'mail.channel', 'image_small')

    convert(cr, 'payment.acquirer', 'image')
    convert(cr, 'payment.acquirer', 'image_medium')
    convert(cr, 'payment.acquirer', 'image_small')

    convert(cr, 'pos.category', 'image')
    convert(cr, 'pos.category', 'image_medium')
    convert(cr, 'pos.category', 'image_small')
    convert(cr, 'restaurant.floor', 'background_image')     # XXX ???

    convert(cr, 'product.template', 'image')
    convert(cr, 'product.template', 'image_medium')
    convert(cr, 'product.template', 'image_small')
    convert(cr, 'product.product', 'image_variant')

    convert(cr, 'ir.header_img', 'img')

    convert(cr, 'event.track', 'image')
    convert(cr, 'event.sponsor', 'image_medium')

    convert(cr, 'product.public.category', 'image')
    convert(cr, 'product.public.category', 'image_medium')
    convert(cr, 'product.public.category', 'image_small')

    convert(cr, 'slide.slide', 'image')
    convert(cr, 'slide.slide', 'image_medium')
    convert(cr, 'slide.slide', 'image_thumb')   # WTF?


if __name__ == '__main__':
    util.main(migrate, 'force')
