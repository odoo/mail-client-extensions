import { Email } from '../models/email'
import { ErrorMessage } from '../models/error_message'
import API from './api'
import { postJsonRpc } from './http'
import { _t } from './translate'

/**
 * Format the email body before sending it to Odoo.
 * Add error message at the end of the email, fix some CSS issues,...
 */
async function _formatEmailBody(email: Email, error: boolean): Promise<string> {
    let body = await email.getBody()

    if (error) {
        body += `<br/><i>${_t(
            'Attachments could not be logged in Odoo because their total size exceeded the allowed maximum.'
        )}</i>`
    }
    return body
}

/**
 * Log the given email body in the chatter of the given record.
 */
export async function logEmail(
    recordId: number,
    recordModel: string,
    email: Email
): Promise<ErrorMessage> {
    const attachments = await email.getAttachments()
    const body = await _formatEmailBody(email, attachments === null)
    const response = await postJsonRpc(API.LOG_EMAIL, {
        body,
        subject: email.subject,
        email_from: email.emailFrom,
        email_to: email.emailTo,
        email_cc: email.emailCC,
        timestamp: email.timestamp,
        res_id: recordId,
        model: recordModel,
        attachments: attachments,
        application_name: _t('Odoo for Outlook'),
    })
    const error = new ErrorMessage()
    if (!response) {
        error.setError('unknown')
    } else {
        setLoggedState(recordId, recordModel, email)
    }
    return error
}

/**
 * Store in the local storage the logged state.
 */
function setLoggedState(recordId: number, recordModel: string, email: Email) {
    const baseUrl = new URL(localStorage.getItem('odoo_url')).host
    let loggedState: string[] = JSON.parse(
        localStorage.getItem('logged_state') || '[]'
    )
    const key = `${baseUrl}-${recordId}-${recordModel}-${email.messageId}`
    loggedState.push(key)
    if (loggedState.length > 5000) {
        // LRU cache, keep only the X last elements
        loggedState = loggedState.slice(
            loggedState.length - 5000,
            loggedState.length
        )
    }
    localStorage.setItem('logged_state', JSON.stringify(loggedState))
}

/**
 * Return true if the current email has been logged on the giver record.
 */
export function getLoggedState(
    recordId: number,
    recordModel: string,
    email: Email
): boolean {
    const baseUrl = new URL(localStorage.getItem('odoo_url')).host
    const loggedState: string[] = JSON.parse(
        localStorage.getItem('logged_state') || '[]'
    )
    const key = `${baseUrl}-${recordId}-${recordModel}-${email.messageId}`
    return loggedState.includes(key)
}
