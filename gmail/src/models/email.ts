import { ErrorMessage } from "../models/error_message";

/**
 * Represent the current email open in the Gmail application.
 */
export class Email {
    accessToken: string;
    messageId: string;
    subject: string;
    body: string;
    timestamp: number;

    emailFrom: string;
    contacts: EmailContact[];

    // When asking for the attachments, a long moment after opening
    // the addon, then the token to get the Gmail Message expired
    // so we cache the result and ask it when loading the app
    _attachmentsParsed: [string[][], ErrorMessage];

    constructor(messageId: string = null, accessToken: string = null) {
        if (messageId) {
            const userEmail = Session.getEffectiveUser().getEmail().toLowerCase();

            this.accessToken = accessToken;

            this.messageId = messageId;
            const message = GmailApp.getMessageById(this.messageId);
            this.subject = message.getSubject();
            this.body = message.getBody();
            this.timestamp = message.getDate().getTime();
            this.emailFrom = message.getFrom();

            this._attachmentsParsed = this.getAttachments();

            this.contacts = [
                ...this._emailSplitTuple(message.getTo(), userEmail),
                ...this._emailSplitTuple(this.emailFrom, userEmail),
                ...this._emailSplitTuple(message.getCc(), userEmail),
                ...this._emailSplitTuple(message.getBcc(), userEmail),
            ];
        }
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
    _emailSplitTuple(fullEmail: string, userEmail: string): EmailContact[] {
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
        const email = new Email();
        email.accessToken = values.accessToken;
        email.messageId = values.messageId;
        email.subject = values.subject;
        email.body = values.body;
        email.timestamp = values.timestamp;
        email.emailFrom = values.emailFrom;
        email.contacts = values.contacts.map((c) => EmailContact.fromJson(c));
        email._attachmentsParsed = [
            values._attachmentsParsed[0],
            ErrorMessage.fromJson(values._attachmentsParsed[1]),
        ];
        return email;
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
    getAttachments(): [string[][], ErrorMessage] {
        if (this._attachmentsParsed) {
            return this._attachmentsParsed;
        }
        GmailApp.setCurrentMessageAccessToken(this.accessToken);
        const message = GmailApp.getMessageById(this.messageId);
        const gmailAttachments = message.getAttachments();
        const attachments: string[][] = [];

        // The size limit of the POST request are 50 MB
        // So we limit the total attachment size to 40 MB
        const MAXIMUM_ATTACHMENTS_SIZE = 40 * 1024 * 1024;

        let totalAttachmentsSize = 0;

        for (const gmailAttachment of gmailAttachments) {
            const bytesSize = gmailAttachment.getSize();
            totalAttachmentsSize += bytesSize;
            if (totalAttachmentsSize > MAXIMUM_ATTACHMENTS_SIZE) {
                return [null, new ErrorMessage("attachments_size_exceeded")];
            }

            const name = gmailAttachment.getName();
            const content = Utilities.base64Encode(gmailAttachment.getBytes());

            attachments.push([name, content]);
        }

        return [attachments, new ErrorMessage(null)];
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
