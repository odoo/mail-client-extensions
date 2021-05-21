# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.convert_binary_field_to_attachment(cr, "ir.ui.menu", "web_icon_data")
    util.convert_binary_field_to_attachment(cr, "res.country", "image")
    util.convert_binary_field_to_attachment(cr, "res.partner", "image")
    util.convert_binary_field_to_attachment(cr, "res.partner", "image_medium")
    util.convert_binary_field_to_attachment(cr, "res.partner", "image_small")

    # process also other modules here (1 place to fix)
    util.convert_binary_field_to_attachment(cr, "fleet.vehicle.model.brand", "image")
    util.convert_binary_field_to_attachment(cr, "fleet.vehicle.model.brand", "image_medium")
    util.convert_binary_field_to_attachment(cr, "fleet.vehicle.model.brand", "image_small")

    util.convert_binary_field_to_attachment(cr, "gamification.badge", "image")

    util.convert_binary_field_to_attachment(cr, "hr.employee", "image")
    util.convert_binary_field_to_attachment(cr, "hr.employee", "image_medium")
    util.convert_binary_field_to_attachment(cr, "hr.employee", "image_small")

    util.convert_binary_field_to_attachment(cr, "im_livechat.channel", "image")
    util.convert_binary_field_to_attachment(cr, "im_livechat.channel", "image_medium")
    util.convert_binary_field_to_attachment(cr, "im_livechat.channel", "image_small")

    util.convert_binary_field_to_attachment(cr, "mail.channel", "image")
    util.convert_binary_field_to_attachment(cr, "mail.channel", "image_medium")
    util.convert_binary_field_to_attachment(cr, "mail.channel", "image_small")

    util.convert_binary_field_to_attachment(cr, "payment.acquirer", "image")
    util.convert_binary_field_to_attachment(cr, "payment.acquirer", "image_medium")
    util.convert_binary_field_to_attachment(cr, "payment.acquirer", "image_small")

    util.convert_binary_field_to_attachment(cr, "pos.category", "image")
    util.convert_binary_field_to_attachment(cr, "pos.category", "image_medium")
    util.convert_binary_field_to_attachment(cr, "pos.category", "image_small")
    util.convert_binary_field_to_attachment(cr, "restaurant.floor", "background_image")  # XXX ???

    util.convert_binary_field_to_attachment(cr, "product.template", "image")
    util.convert_binary_field_to_attachment(cr, "product.template", "image_medium")
    util.convert_binary_field_to_attachment(cr, "product.template", "image_small")
    util.convert_binary_field_to_attachment(cr, "product.product", "image_variant")

    util.convert_binary_field_to_attachment(cr, "ir.header_img", "img")

    util.convert_binary_field_to_attachment(cr, "event.track", "image")
    util.convert_binary_field_to_attachment(cr, "event.sponsor", "image_medium")

    util.convert_binary_field_to_attachment(cr, "product.public.category", "image")
    util.convert_binary_field_to_attachment(cr, "product.public.category", "image_medium")
    util.convert_binary_field_to_attachment(cr, "product.public.category", "image_small")

    util.convert_binary_field_to_attachment(cr, "slide.slide", "image")
    util.convert_binary_field_to_attachment(cr, "slide.slide", "image_medium")
    util.convert_binary_field_to_attachment(cr, "slide.slide", "image_thumb")  # WTF?
