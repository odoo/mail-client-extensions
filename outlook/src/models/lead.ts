import API from '../helpers/api'
import { postJsonRpc } from '../helpers/http'
import { Partner } from './partner'

/**
 * Represent a "crm.lead" record.
 */
export class Lead {
    id: number
    name: string
    revenuesDescription: string

    /**
     * Make a RPC call to the Odoo database to create a lead
     */
    static async createLead(
        partner: Partner,
        emailBody: string,
        emailSubject: string
    ): Promise<[Lead, Partner] | null> {
        const response = await postJsonRpc(API.CREATE_LEAD, {
            email_body: emailBody,
            email_subject: emailSubject,
            partner_id: partner.id,
            partner_email: partner.email,
            partner_name: partner.name,
        })

        if (!response?.id) {
            return null
        }

        const newPartner = partner.clone()
        if (!partner.id) {
            newPartner.id = response.partner_id
            newPartner.image = response.partner_image
            newPartner.isWritable = true
        }
        return [Lead.fromOdooResponse(response), newPartner]
    }

    /**
     * Parse the dictionary returned by the Odoo database endpoint.
     */
    static fromOdooResponse(values: any): Lead {
        const lead = new Lead()
        lead.id = values.id
        lead.name = values.name
        lead.revenuesDescription = values.revenues_description
        return lead
    }
}
