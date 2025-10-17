import API from '../helpers/api'
import { postJsonRpc } from '../helpers/http'
import { _t } from '../helpers/translate'
import { ErrorMessage } from '../models/error_message'
import { Lead } from './lead'
import { Task } from './task'
import { Ticket } from './ticket'

/**
 * Represent the current partner and all the information about him.
 */
export class Partner {
    id: number
    name: string
    email: string

    image: string
    isCompany: boolean
    companyName: string
    phone: string
    mobile: string

    leads: Lead[]
    leadCount: number
    tickets: Ticket[]
    ticketCount: number
    tasks: Task[]
    taskCount: number

    isWritable: boolean
    canCreateProject: boolean
    canCreatePartner: boolean

    get description() {
        return this.id ? this.email : _t('New Person')
    }

    /**
     * Key used to force the re-rendering when one of the elements changed.
     */
    get key() {
        return `partner-${this.id}-${this.leads?.length}-${this.tickets?.length}-${this.tasks?.length}`
    }

    /**
     * Clone the partner.
     */
    clone(): Partner {
        const newPartner = new Partner()
        for (const key of Object.keys(this)) {
            const value = this[key]
            if (Array.isArray(value)) {
                newPartner[key] = [...value]
            } else {
                newPartner[key] = value
            }
        }
        return newPartner
    }

    /**
     * Parse the response of the Odoo database.
     */
    static fromOdooResponse(values: any): Partner {
        const partner = new Partner()

        partner.id = values.id
        partner.name = values.name
        partner.email = values.email

        partner.image = values.image || 'assets/person.png'
        partner.isCompany = values.is_company
        partner.isCompany = values.is_company
        partner.companyName = values.company_name

        partner.phone = values.phone
        partner.mobile = values.mobile
        partner.isWritable = values.can_write_on_partner

        return partner
    }

    /**
     * Create a "res.partner" with the given values in the Odoo database.
     */
    static async savePartner(partner: Partner): Promise<Partner | null> {
        const partnerValues = {
            name: partner.name,
            email: partner.email,
        }

        const response = await postJsonRpc(API.PARTNER_CREATE, partnerValues)

        if (!response?.id) {
            return null
        }

        const newPartner = partner.clone()
        newPartner.id = response.id
        newPartner.image = response.image
        newPartner.isWritable = true
        return newPartner
    }

    /**
     * Fetch the given partner on the Odoo database and return all information about him.
     *
     * Return
     *      - The Partner related to the given email address
     *      - The list of Odoo companies in which the current user belongs
     *      - True if the current user can create partner in his Odoo database
     *      - True if the current user can create projects in his Odoo database
     *      - The error message if something bad happened
     */
    static async getPartner(
        name: string,
        email: string,
        partnerId: number = null
    ): Promise<[Partner, ErrorMessage]> {
        const response = await postJsonRpc(API.GET_PARTNER, {
            email: email,
            partner_id: partnerId,
        })

        if (response && response.error) {
            const error = new ErrorMessage('odoo', response.error)
            const partner = Partner.fromOdooResponse({ name, email })
            return [partner, error]
        }

        if (!response || !response.partner) {
            const error = new ErrorMessage('http_error_odoo')
            const partner = Partner.fromOdooResponse({ name, email })
            return [partner, error]
        }

        const error = new ErrorMessage()
        const partner = Partner.fromOdooResponse({
            name,
            email,
            ...response.partner,
        })

        // Parse leads
        if (response.leads) {
            partner.leadCount = response.lead_count
            partner.leads = response.leads.map((leadValues: any) =>
                Lead.fromOdooResponse(leadValues)
            )
        }

        // Parse tickets
        if (response.tickets) {
            partner.ticketCount = response.ticket_count
            partner.tickets = response.tickets.map((ticketValues: any) =>
                Ticket.fromOdooResponse(ticketValues)
            )
        }

        // Parse tasks
        if (response.tasks) {
            partner.taskCount = response.task_count
            partner.tasks = response.tasks.map((taskValues: any) =>
                Task.fromOdooResponse(taskValues)
            )
        }
        partner.canCreateProject = response.can_create_project !== false

        // undefined must be considered as true
        partner.canCreatePartner = response.can_create_partner !== false

        return [partner, error]
    }

    /**
     * Perform a search on the Odoo database and return the list of matched partners.
     */
    static async searchPartner(
        query: string | string[]
    ): Promise<[Partner[], ErrorMessage]> {
        const response = await postJsonRpc(API.SEARCH_PARTNER, { query })

        if (!response?.length) {
            return [[], new ErrorMessage('http_error_odoo')]
        }

        return [
            response[0].map((values: any) => Partner.fromOdooResponse(values)),
            new ErrorMessage(),
        ]
    }
}
