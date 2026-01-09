import API from '../helpers/api'
import { postJsonRpc } from '../helpers/http'
import { ErrorMessage } from './error_message'
import { OdooRecord } from './odoo'

/**
 * Represent a "project.project" record.
 */
export class Project extends OdooRecord {
    partnerName: string
    stageName: string
    companyName: string
    description: string

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: Record<string, any>): Project {
        const project = new Project()
        project.id = values.id
        project.name = values.name
        project.partnerName = values.partner_name
        project.stageName = values.stage_name
        project.companyName = values.company_name
        const description = [
            project.companyName,
            project.partnerName,
            project.stageName,
        ]
        project.description = description.filter((l) => l).join(' - ')
        return project
    }

    /**
     * Make a RPC call to the Odoo database to search a project.
     */
    static async searchProject(
        query: string
    ): Promise<[Project[], ErrorMessage]> {
        const response = await postJsonRpc(API.SEARCH_PROJECT, { query })

        if (!response?.length) {
            return [[], new ErrorMessage('http_error_odoo')]
        }

        return [
            response[0].map((values: Record<string, any>) =>
                Project.fromOdooResponse(values)
            ),
            new ErrorMessage(),
        ]
    }

    /**
     * Make a RPC call to the Odoo database to create a project
     * and return the newly created record.
     */
    static async createProject(name: string): Promise<Project> {
        const response = await postJsonRpc(API.CREATE_PROJECT, { name: name })

        const projectId = response ? response.id || null : null
        if (!projectId) {
            return null
        }

        return Project.fromOdooResponse({
            id: projectId,
            name: response.name,
        })
    }
}
