import { URLS } from "../consts";
import { postJsonRpc } from "../utils/http";
import { Email } from "./email";
import { Partner } from "./partner";
import { User } from "./user";

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
    static async createTask(
        user: User,
        partner: Partner,
        projectId: number,
        email: Email,
    ): Promise<[Task, Partner] | null> {
        const [body, _, attachmentsParsed] = await email.getBodyAndAttachments();
        const response = await postJsonRpc(
            user.odooUrl + URLS.CREATE_TASK,
            {
                email_body: body,
                email_subject: email.subject,
                partner_email: partner.email,
                partner_id: partner.id,
                partner_name: partner.name,
                project_id: projectId,
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
        return [Task.fromOdooResponse(response), partner];
    }
}
