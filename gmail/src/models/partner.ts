import { Lead } from "./lead";
import { Task } from "./task";
import { Ticket } from "./ticket";
import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { ErrorMessage } from "../models/error_message";
import { getAccessToken } from "src/services/odoo_auth";
import { getOdooServerUrl } from "src/services/app_properties";
import { UI_ICONS } from "../views/icons";

/**
 * Represent the current partner and all the information about him.
 */
export class Partner {
    id: number;
    name: string;
    email: string;

    image: string;
    isCompany: boolean;
    parentName: string;
    phone: string;
    mobile: string;

    leads: Lead[];
    leadCount: number;
    tickets: Ticket[];
    ticketCount: number;
    tasks: Task[];
    taskCount: number;

    isWritable: boolean;

    /**
     * Return the image to show in the interface for the current partner.
     */
    getImage() {
        if (!this.id || this.id < 0 || !this.image) {
            return UI_ICONS.person;
        }
        return this.image;
    }

    /**
     * Unserialize the partner object (reverse JSON.stringify).
     */
    static fromJson(values: any): Partner {
        const partner = new Partner();

        partner.id = values.id;
        partner.name = values.name;
        partner.email = values.email;

        partner.image = values.image;
        partner.isCompany = values.isCompany;
        partner.parentName = values.parentName;
        partner.phone = values.phone;
        partner.mobile = values.mobile;

        partner.leadCount = values.leadCount;
        partner.ticketCount = values.ticketCount;
        partner.taskCount = values.taskCount;

        partner.isWritable = values.isWritable;

        partner.leads = values.leads
            ? values.leads.map((leadValues: any) => Lead.fromJson(leadValues))
            : null;

        partner.tickets = values.tickets
            ? values.tickets.map((ticketValues: any) => Ticket.fromJson(ticketValues))
            : null;

        partner.tasks = values.tasks
            ? values.tasks.map((taskValues: any) => Task.fromJson(taskValues))
            : null;

        return partner;
    }

    static fromOdooResponse(values: any): Partner {
        const partner = new Partner();

        if (values.id && values.id > 0) {
            partner.id = values.id;
        }
        partner.name = values.name;
        partner.email = values.email;

        partner.image = values.image;
        partner.isCompany = values.is_company;
        partner.isCompany = values.is_company;
        partner.parentName = values.parent_name;

        partner.phone = values.phone;
        partner.mobile = values.mobile;
        partner.isWritable = values.can_write_on_partner;

        return partner;
    }

    /**
     * Create a "res.partner" with the given values in the Odoo database.
     */
    static savePartner(partner: Partner): Partner | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.PARTNER_CREATE;
        const odooAccessToken = getAccessToken();

        const partnerValues = {
            name: partner.name,
            email: partner.email,
        };

        const response = postJsonRpc(url, partnerValues, {
            Authorization: "Bearer " + odooAccessToken,
        });

        if (!response?.id) {
            return null;
        }
        partner.id = response.id;
        partner.image = response.image;
        partner.isWritable = true;
        return partner;
    }

    /**
     * Fetch the given partner on the Odoo database and return all information about him.
     *
     * Return
     *      - The Partner related to the given email address
     *      - True if the current user can create partner in his Odoo database
     *      - True if the current user can create projects in his Odoo database
     *      - The error message if something bad happened
     */
    static getPartner(
        name: string,
        email: string,
        partnerId: number = null,
    ): [Partner, boolean, boolean, ErrorMessage] {
        const odooServerUrl = getOdooServerUrl();
        const odooAccessToken = getAccessToken();

        if (!odooServerUrl || !odooAccessToken) {
            const error = new ErrorMessage("http_error_odoo");
            const partner = Partner.fromJson({ name, email });
            return [partner, false, false, error];
        }

        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.GET_PARTNER;

        const response = postJsonRpc(
            url,
            { email: email, partner_id: partnerId },
            { Authorization: "Bearer " + odooAccessToken },
        );

        if (response && response.error) {
            const error = new ErrorMessage("odoo", response.error);
            const partner = Partner.fromJson({ name, email });
            return [partner, false, false, error];
        }

        if (!response || !response.partner) {
            const error = new ErrorMessage("http_error_odoo");
            const partner = Partner.fromJson({ name, email });
            return [partner, false, false, error];
        }

        const error = new ErrorMessage();
        const partner = Partner.fromOdooResponse({ name, email, ...response.partner });

        // Parse leads
        if (response.leads) {
            partner.leadCount = response.lead_count;
            partner.leads = response.leads.map((leadValues: any) =>
                Lead.fromOdooResponse(leadValues),
            );
        }

        // Parse tickets
        if (response.tickets) {
            partner.ticketCount = response.ticket_count;
            partner.tickets = response.tickets.map((ticketValues: any) =>
                Ticket.fromOdooResponse(ticketValues),
            );
        }

        // Parse tasks
        if (response.tasks) {
            partner.taskCount = response.task_count;
            partner.tasks = response.tasks.map((taskValues: any) =>
                Task.fromOdooResponse(taskValues),
            );
        }
        const canCreateProject = response.can_create_project !== false;

        // undefined must be considered as true
        const canCreatePartner = response.can_create_partner !== false;

        return [partner, canCreatePartner, canCreateProject, error];
    }

    /**
     * Perform a search on the Odoo database and return the list of matched partners.
     */
    static searchPartner(query: string | string[]): [Partner[], ErrorMessage] {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.SEARCH_PARTNER;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            { query },
            { Authorization: "Bearer " + odooAccessToken },
        );

        if (!response?.length) {
            return [[], new ErrorMessage("http_error_odoo")];
        }

        return [
            response[0].map((values: any) => Partner.fromOdooResponse(values)),
            new ErrorMessage(),
        ];
    }
}
