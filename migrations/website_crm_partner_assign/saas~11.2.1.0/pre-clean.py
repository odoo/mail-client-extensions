# -*- coding: utf-8 -*-

def migrate(cr, version):
    # clean wizard to allow mail template to be updated. See https://git.io/vxVjA
    cr.execute("DELETE FROM crm_lead_assignation")
    cr.execute("DELETE FROM crm_lead_forward_to_partner")
