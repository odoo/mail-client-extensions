# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(cr, "mass_mailing.mass_mail_list_1")

    util.create_column(cr, "mail_mass_mailing", "subject", "varchar")
    util.create_column(cr, "mail_mass_mailing", "body_arch", "text")
    cr.execute("""
        UPDATE mail_mass_mailing m
           SET subject=u.name
          FROM utm_source u
         WHERE u.id=m.source_id;
    """)
    cr.execute("""
    INSERT INTO ir_translation (lang, src, type, res_id, value, name, module, state)
        SELECT i.lang,i.src,i.type,m.id,i.value,'mail.mass_mailing,subject',i.module,i.state
          FROM ir_translation i
    INNER JOIN mail_mass_mailing m on m.source_id=i.res_id and i.name='utm.source,name';
    """)
    util.remove_view(cr, "mass_mailing.FieldTextHtmlInline")
    util.remove_view(cr, "mass_mailing.FieldTextHtmlPopupContent")
