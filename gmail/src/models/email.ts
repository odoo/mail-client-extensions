import { OAuth2Client } from "google-auth-library";
import { google } from "googleapis";
import { simpleParser } from "mailparser";
import { ErrorMessage } from "../models/error_message";
import pool from "../utils/db";
import { User } from "./user";

const gmail = google.gmail({ version: "v1" });

/**
 * Represent the current email open in the Gmail application.
 */
export class Email {
    userOAuthToken: string;
    accessToken: string;
    messageId: string;
    subject: string;

    emailFrom: string;
    emailTo: string;
    emailCC: string;
    contacts: EmailContact[];

    // Store on which record the current email has been logged
    // >>> {"res.partner": [1, 2, 3]}
    loggingState: Record<string, number[]>;

    constructor(
        userOAuthToken: string,
        accessToken: string,
        messageId: string,
        subject: string,
        emailFrom: string,
        emailTo: string,
        emailCC: string,
        contacts: EmailContact[],
        loggingState: Record<string, number[]>,
    ) {
        this.userOAuthToken = userOAuthToken;
        this.accessToken = accessToken;
        this.messageId = messageId;
        this.subject = subject;
        this.emailFrom = emailFrom;
        this.emailTo = emailTo;
        this.emailCC = emailCC;
        this.contacts = contacts;
        this.loggingState = loggingState;
    }

    /**
     * Use the token we receive from Google to get the information about the opened email.
     *
     * Only get the headers of the email to not slow down the application
     * (if we don't log the email, we only need the contacts that are in
     * the email, we can delay the fetching of the email body and
     * the attachments).
     */
    static async getEmailHeadersFromGoogleToken(event: any): Promise<Record<string, string>> {
        const messageId = event.gmail.messageId;
        const auth = new OAuth2Client();
        auth.setCredentials({ access_token: event.authorizationEventObject.userOAuthToken });
        // @ts-ignore
        const gmailResponse = await gmail.users.messages.get({
            id: messageId,
            userId: "me",
            format: "metadata",
            auth,
            headers: { "X-Goog-Gmail-Access-Token": event.gmail.accessToken },
        });
        // @ts-ignore
        const rawHeaders = gmailResponse.data.payload.headers;
        return Object.fromEntries(rawHeaders.map((h) => [h.name.toLowerCase(), h.value]));
    }

    /**
     * Once we got the headers and the user from the Gmail API,
     * we can build the `Email` object.
     */
    static async getEmailFromHeaders(
        event: any,
        headers: Record<string, string>,
        user: User,
    ): Promise<Email> {
        const userEmail = user.email.toLowerCase();
        const contacts = [
            ...this._emailSplitTuple(headers["to"] || "", userEmail),
            ...this._emailSplitTuple(headers["from"] || "", userEmail),
            ...this._emailSplitTuple(headers["cc"] || "", userEmail),
            ...this._emailSplitTuple(headers["bcc"] || "", userEmail),
        ];

        return new Email(
            event.authorizationEventObject.userOAuthToken,
            event.gmail.accessToken,
            event.gmail.messageId,
            headers["subject"] || "",
            headers["from"] || "",
            headers["to"] || "",
            headers["cc"] || "",
            contacts,
            await this._getLoggingState(user, event.gmail.messageId),
        );
    }

    /**
     * Fetch the information in the email that require the full EML.
     */
    async getBodyAndAttachments(): Promise<[string, number, [string[][], ErrorMessage]]> {
        const auth = new OAuth2Client();
        auth.setCredentials({ access_token: this.userOAuthToken });

        // @ts-ignore
        const gmailResponse = await gmail.users.messages.get({
            id: this.messageId,
            userId: "me",
            format: "raw",
            auth,
            headers: { "X-Goog-Gmail-Access-Token": this.accessToken },
        });

        // @ts-ignore
        const messageEmlB64 = gmailResponse.data.raw;
        const messageEml = atob(messageEmlB64.replaceAll("-", "+").replaceAll("_", "/"));

        const mail = await simpleParser(messageEml);
        return [
            mail.html || mail.text || "",
            mail.date.getTime(),
            this._getAttachments(mail.attachments),
        ];
    }

    /**
     * Parse a full FROM header and return the name and email parts.
     *
     * E.G.
     * "BOB" <bob@example.com>
     * => [["BOB", "bob@example.com"]]
     *
     * bob@example.com
     * => [["bob@example.com", "bob@example.com"]]
     *
     * alice@example.com, bob@example.com
     * => [
     *      ["alice@example.com", "alice@example.com"],
     *      ["bob@example.com", "bob@example.com"]
     * ]
     *
     * "Alice" <alice@example.com>, "BOB" <bob@example.com>
     *  => [
     *      ["alice@example.com", "alice@example.com"],
     *      ["bob@example.com", "bob@example.com"]
     * ]
     *
     * <alice@example.com>, <bob@example.com>
     * => [
     *      ["alice@example.com", "alice@example.com"],
     *      ["bob@example.com", "bob@example.com"]
     * ]
     */
    private static _emailSplitTuple(fullEmail: string, userEmail: string): EmailContact[] {
        const contacts = [];
        const re = /(.*?)<(.*?)>/;
        for (const part of fullEmail.split(",")) {
            if (part.toLowerCase().indexOf(userEmail) >= 0 || !part.trim()?.length) {
                // Skip the user's email
                continue;
            }

            const result = part.match(re);
            if (!result) {
                contacts.push(new EmailContact(part.trim(), part.trim(), part.trim()));
                continue;
            }
            const email = result[2].trim();
            let name = result[1].replace(/\"/g, "").trim() || email;
            contacts.push(new EmailContact(name, email, part.trim()));
        }
        return contacts;
    }

    /**
     * Unserialize the email object (reverse JSON.stringify).
     */
    static fromJson(values: any): Email {
        return new Email(
            values.userOAuthToken,
            values.accessToken,
            values.messageId,
            values.subject,
            values.emailFrom,
            values.emailTo,
            values.emailCC,
            values.contacts.map((c) => EmailContact.fromJson(c)),
            values.loggingState,
        );
    }

    /**
     * Return the list of the attachments in the email.
     * Done in a getter and not as a property because this object is serialized and
     * given to the event handler.
     *
     * Returns:
     *     - Null and "attachments_size_exceeded" error, if the total attachment size limit
     *       is exceeded so we do not keep big files in memory.
     *     - If no attachment, return an empty array and an empty error message.
     *     - Otherwise, the list of attachments base 64 encoded and an empty error message
     */
    private _getAttachments(gmailAttachments): [string[][], ErrorMessage] {
        const attachments: string[][] = [];

        // The size limit of the POST request are 50 MB
        // So we limit the total attachment size to 40 MB
        const MAXIMUM_ATTACHMENTS_SIZE = 40 * 1024 * 1024;

        let totalAttachmentsSize = 0;

        for (const gmailAttachment of gmailAttachments) {
            if (gmailAttachment.contentDisposition === "inline") {
                // Outlook inline images
                continue;
            }
            const bytesSize = gmailAttachment.content.length;
            totalAttachmentsSize += bytesSize;
            if (totalAttachmentsSize > MAXIMUM_ATTACHMENTS_SIZE) {
                return [null, new ErrorMessage("attachments_size_exceeded")];
            }
            const name = gmailAttachment.filename;
            const content = gmailAttachment.content.toString("base64");

            attachments.push([name, content]);
        }

        return [attachments, new ErrorMessage(null)];
    }

    /**
     * Save the fact that we logged the email on the record, in the cache.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    async setLoggingState(user: User, resModel: string, resId: number) {
        console.log(`Logging email for user ${user.email}`)
        this.loggingState[resModel].push(resId);
        await pool.query(
            `
            INSERT INTO email_logs (user_id, message_id, res_id, res_model)
                 VALUES ($1, $2, $3, $4)
            `,
            [user.id, this.messageId, resId, resModel],
        );
    }

    /**
     * Check if the email has not been logged on the record.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    checkLoggingState(resModel: string, resId: number): boolean {
        return this.loggingState[resModel].includes(resId);
    }

    /**
     * Get the logging state for the current email
     * (that way, we do only one query for all the records we will see),
     */
    private static async _getLoggingState(
        user: User,
        messageId: string,
    ): Promise<Record<string, number[]>> {
        const result = await pool.query(
            `
                SELECT res_model, res_id
                  FROM email_logs
                 WHERE user_id = $1 AND message_id = $2
            `,
            [user.id, messageId],
        );
        const ret: Record<string, number[]> = {
            "res.partner": [],
            "crm.lead": [],
            "helpdesk.ticket": [],
            "project.task": [],
        };
        for (const row of result.rows) {
            ret[row.res_model].push(row.res_id);
        }
        return ret;
    }
}

export class EmailContact {
    name: string;
    email: string;
    fullEmail: string;

    constructor(name: string, email: string, fullEmail: string) {
        this.name = name;
        this.email = email;
        this.fullEmail = fullEmail;
    }

    static fromJson(values: any): EmailContact {
        return new EmailContact(values.name, values.email, values.fullEmail);
    }
}
