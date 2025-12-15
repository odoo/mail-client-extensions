import * as crypto from "crypto";
import { OAuth2Client } from "google-auth-library";
import { CLIENT_ID } from "../consts";
import pool from "../utils/db";

export class User {
    id?: number;
    email: string;
    odooUrl?: string;
    odooToken?: string;

    // That token is used to authenticate the user when he's redirected
    // to the callback URL, and can be used only once
    loginToken?: string;
    loginTokenExpireAt?: Date;

    // Store the translation for the current user, based on the language
    // of his `res.users` on the Odoo side
    translations?: any;
    translationsExpireAt?: Date;

    constructor(
        id: number,
        email: string,
        odooUrl?: string,
        odooToken?: string,
        loginToken?: string,
        loginTokenExpireAt?: Date,
        translations?: any,
        translationsExpireAt?: Date,
    ) {
        this.id = id;
        this.email = email;
        this.odooUrl = odooUrl;
        this.odooToken = odooToken;
        this.loginToken = loginToken;
        this.loginTokenExpireAt = loginTokenExpireAt;
        this.translations = translations;
        this.translationsExpireAt = translationsExpireAt;
    }

    async save() {
        console.log(`Saving user ${this.email}`)
        await pool.query(
            `
                INSERT INTO users_settings (
                                email,
                                odoo_url,
                                odoo_token,
                                login_token,
                                login_token_expire_at,
                                translations,
                                translations_expire_at
                            )
                     VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (email) DO UPDATE
                        SET odoo_url = EXCLUDED.odoo_url,
                            odoo_token = EXCLUDED.odoo_token,
                            login_token = EXCLUDED.login_token,
                            login_token_expire_at = EXCLUDED.login_token_expire_at,
                            translations = EXCLUDED.translations,
                            translations_expire_at = EXCLUDED.translations_expire_at
            `,
            [
                this.email,
                this.odooUrl,
                this.odooToken,
                this.loginToken,
                this.loginTokenExpireAt,
                this.translations,
                this.translationsExpireAt,
            ],
        );
    }

    /**
     * Generate the login token and set the expiration date in 1 hour.
     */
    async generateLoginToken(): Promise<string> {
        const EXPIRATION_DURATION_MS = 60 * 60 * 1000;
        this.loginTokenExpireAt = new Date(Date.now() + EXPIRATION_DURATION_MS);
        this.loginToken = crypto.randomBytes(64).toString("hex");
        await this.save();
        return this.loginToken;
    }

    /**
     * Check the token we receive from Google, and get the user based on the email.
     */
    static async getUserFromGoogleToken(event: any): Promise<User> {
        const oAuth2Client = new OAuth2Client();
        const decodedToken = await oAuth2Client.verifyIdToken({
            idToken: event.authorizationEventObject.userIdToken,
            audience: CLIENT_ID,
        });
        const payload = decodedToken.getPayload();
        if (!payload.email || !payload.email_verified) {
            throw new Error("Failed to authenticate the user");
        }
        return await User._getUserFromEmail(payload.email);
    }

    /**
     * Check the token we receive from the user's browser, and get the user.
     *
     * The login token can only be used once, and is reset after getting the user.
     */
    static async getUserFromLoginToken(email: string, loginToken: string): Promise<User> {
        const user = await User._getUserFromEmail(email);

        // constant time comparison
        if (!loginToken?.length || loginToken?.length !== user.loginToken?.length) {
            throw new Error("Invalid login token");
        }
        const userTokenA = Buffer.from(loginToken);
        const userTokenB = Buffer.from(user.loginToken);
        if (!crypto.timingSafeEqual(userTokenA, userTokenB)) {
            throw new Error("Invalid login token");
        }
        if (!user.loginTokenExpireAt || new Date() > user.loginTokenExpireAt) {
            throw new Error("Login token expired");
        }

        user.loginToken = undefined;
        user.loginTokenExpireAt = undefined;
        await user.save();

        return user;
    }

    /**
     * Check the login token, and if it's valid, then save the odoo token
     * we received in the callback endpoint.
     */
    async setOdooToken(odooToken: string) {
        if (!odooToken?.length) {
            throw new Error("Empty Odoo token");
        }
        this.odooToken = odooToken;
        await this.save();
    }

    private static async _getUserFromEmail(email: string): Promise<User> {
        const result = await pool.query(
            `
                SELECT id,
                       email,
                       odoo_url,
                       odoo_token,
                       login_token,
                       login_token_expire_at,
                       translations,
                       translations_expire_at
                  FROM users_settings
                 WHERE email = $1
            `,
            [email],
        );
        if (result.rows.length === 0) {
            return new User(null, email);
        }

        const data = result.rows[0];
        return new User(
            data.id,
            email,
            data.odoo_url,
            data.odoo_token,
            data.login_token,
            data.login_token_expire_at,
            data.translations,
            data.translations_expire_at,
        );
    }
}
