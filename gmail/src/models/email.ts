/**
 * Represent the current email open in the Gmail application.
 */
export class Email {
    messageId: string;
    subject: string;

    body: string;
    contactEmail: string;
    contactFullEmail: string;
    contactName: string;

    constructor(messageId: string = null) {
        if (messageId) {
            const userEmail = Session.getEffectiveUser().getEmail().toLowerCase();

            this.messageId = messageId;
            const message = GmailApp.getMessageById(this.messageId);
            this.subject = message.getSubject();

            this.body = message.getBody();

            const fromHeaders = message.getFrom();
            const sent = fromHeaders.toLowerCase().indexOf(userEmail) >= 0;
            this.contactFullEmail = sent ? message.getTo() : message.getFrom();
            [this.contactName, this.contactEmail] = this._emailSplitTuple(this.contactFullEmail);
        }
    }

    /**
     * Parse a full FROM header and return the name part and the email part.
     *
     * E.G.
     *     "BOB" <bob@example.com> => ["BOB", "bob@example.com"]
     *     bob@example.com         => ["bob@example.com", "bob@example.com"]
     *
     */
    _emailSplitTuple(fullEmail: string): [string, string] {
        const match = fullEmail.match(/(.*)\s*<(.*)>/);
        fullEmail = fullEmail.replace("<", "").replace(">", "");

        if (!match) {
            return [fullEmail, fullEmail];
        }

        const [_, name, email] = match;

        if (!name || !email) {
            return [fullEmail, fullEmail];
        }

        return [name.replace(/\"/g, ""), email];
    }

    /**
     * Unserialize the email object (reverse JSON.stringify).
     */
    static fromJson(values: any): Email {
        const email = new Email();

        email.messageId = values.messageId;
        email.subject = values.subject;

        email.body = values.body;
        email.contactEmail = values.contactEmail;
        email.contactFullEmail = values.contactFullEmail;
        email.contactName = values.contactName;

        return email;
    }
}
