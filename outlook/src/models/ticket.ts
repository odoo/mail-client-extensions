import API from '../helpers/api'
import { postJsonRpc } from '../helpers/http'
import { Partner } from './partner'

/**
 * Represent a "helpdesk.ticket" record.
 */
export class Ticket {
    id: number
    name: string
    stageName: string

    /**
     * Make a RPC call to the Odoo database to create a ticket
     */
    static async createTicket(
        partner: Partner,
        emailBody: string,
        emailSubject: string
    ): Promise<[Ticket, Partner] | null> {
        const response = await postJsonRpc(API.CREATE_TICKET, {
            email_body: emailBody,
            email_subject: emailSubject,
            partner_email: partner.email,
            partner_id: partner.id,
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
        return [Ticket.fromOdooResponse(response), newPartner]
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Ticket {
        const ticket = new Ticket()
        ticket.id = values.id
        ticket.name = values.name
        ticket.stageName = values.stage_name
        return ticket
    }
}
