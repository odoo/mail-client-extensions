import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";
import { Partner } from "./partner";

/**
 * Represent a "project.task" record.
 */
export class Task {
    id: number;
    name: string;
    projectName: string;

    /**
     * Unserialize the task object (reverse JSON.stringify).
     */
    static fromJson(values: any): Task {
        const task = new Task();
        task.id = values.id;
        task.name = values.name;
        task.projectName = values.projectName;
        return task;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Task {
        const task = new Task();
        task.id = values.id;
        task.name = values.name;
        task.projectName = values.project_name;
        return task;
    }

    /**
     * Make a RPC call to the Odoo database to create a task
     * and return the ID of the newly created record.
     */
    static createTask(
        partner: Partner,
        projectId: number,
        emailBody: string,
        emailSubject: string,
    ): [Task, Partner] | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.CREATE_TASK;
        const odooAccessToken = getAccessToken();
        const response = postJsonRpc(
            url,
            {
                email_body: emailBody,
                email_subject: emailSubject,
                partner_email: partner.email,
                partner_id: partner.id,
                partner_name: partner.name,
                project_id: projectId,
            },
            { Authorization: "Bearer " + odooAccessToken },
        );
        if (!response?.id) {
            return null;
        }
        if (!partner.id) {
            partner.id = response.partner_id;
            partner.image = response.partner_image;
        }
        return [Task.fromOdooResponse(response), partner];
    }
}
