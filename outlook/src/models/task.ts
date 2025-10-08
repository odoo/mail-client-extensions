import API from '../helpers/api'
import { postJsonRpc } from '../helpers/http'
import { Partner } from './partner'

/**
 * Represent a "project.task" record.
 */
export class Task {
    id: number
    name: string
    projectName: string

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Task {
        const task = new Task()
        task.id = values.id
        task.name = values.name
        task.projectName = values.project_name
        return task
    }

    /**
     * Make a RPC call to the Odoo database to create a task
     */
    static async createTask(
        partner: Partner,
        projectId: number,
        emailBody: string,
        emailSubject: string
    ): Promise<[Task, Partner] | null> {
        const response = await postJsonRpc(API.CREATE_TASK, {
            email_body: emailBody,
            email_subject: emailSubject,
            partner_email: partner.email,
            partner_id: partner.id,
            partner_name: partner.name,
            project_id: projectId,
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
        return [Task.fromOdooResponse(response), newPartner]
    }
}
