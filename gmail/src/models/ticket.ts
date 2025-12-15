import { URLS } from "../consts";
import { postJsonRpc } from "../utils/http";
import { Email } from "./email";
import { Partner } from "./partner";
import { User } from "./user";

/**
 * Represent a "helpdesk.ticket" record.
 */
export class Ticket {
    id: number;
    name: string;
    stageName: string;

    /**
     * Make a RPC call to the Odoo database to create a ticket
     * and return the ID of the newly created record.
     */
    static async createTicket(
        user: User,
        partner: Partner,
        email: Email,
    ): Promise<[Ticket, Partner] | null> {
        const [body, _, attachmentsParsed] = await email.getBodyAndAttachments();
        const response = await postJsonRpc(
            user.odooUrl + URLS.CREATE_TICKET,
            {
                email_body: body,
                email_subject: email.subject,
                partner_email: partner.email,
                partner_id: partner.id,
                partner_name: partner.name,
                attachments: attachmentsParsed[0],
            },
            { Authorization: "Bearer " + user.odooToken },
        );

        if (!response?.id) {
            return null;
        }
        if (!partner.id) {
            partner.id = response.partner_id;
            partner.image = response.partner_image;
            partner.isWritable = true;
        }
        return [Ticket.fromOdooResponse(response), partner];
    }

    /**
     * Unserialize the ticket object (reverse JSON.stringify).
     */
    static fromJson(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        ticket.stageName = values.stageName;
        return ticket;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        ticket.stageName = values.stage_name;
        return ticket;
    }
}
