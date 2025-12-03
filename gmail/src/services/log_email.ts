import { postJsonRpc } from "../utils/http";
import { escapeHtml } from "../utils/html";
import { URLS } from "../const";
import { Email } from "../models/email";
import { ErrorMessage } from "../models/error_message";
import { _t } from "../services/translation";
import { getAccessToken } from "./odoo_auth";

/**
 * Format the email body before sending it to Odoo.
 * Add error message at the end of the email, fix some CSS issues,...
 */
function _formatEmailBody(email: Email, error: ErrorMessage): string {
    let body = email.body;
    if (error.code === "attachments_size_exceeded") {
        body += `<br/><i>${_t(
            "Attachments could not be logged in Odoo because their total size exceeded the allowed maximum.",
        )}</i>`;
    }

    // Make the "attachment" links bigger, otherwise we need to scroll to fully see them
    // Can not add a <style/> tag because they are sanitized by Odoo
    body = body.replace(
        /class=\"gmail_chip gmail_drive_chip" style=\"/g,
        'class="gmail_chip gmail_drive_chip" style=" min-height: 32px;',
    );
    return body;
}

/**
 * Log the given email body in the chatter of the given record.
 */
export function logEmail(recordId: number, recordModel: string, email: Email): ErrorMessage {
    const odooAccessToken = getAccessToken();
    const [attachments, error] = email.getAttachments();
    const body = _formatEmailBody(email, error);
    const url =
        PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.LOG_EMAIL;

    const response = postJsonRpc(
        url,
        {
            body,
            res_id: recordId,
            model: recordModel,
            attachments: attachments,
            email_from: email.emailFrom,
            subject: email.subject,
            timestamp: email.timestamp,
            application_name: _t("Odoo for Gmail"),
        },
        { Authorization: "Bearer " + odooAccessToken },
    );

    if (!response) {
        error.setError("unknown");
    }

    return error;
}
