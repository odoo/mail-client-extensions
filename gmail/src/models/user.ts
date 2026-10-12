import * as crypto from "crypto";
import { OAuth2Client } from "google-auth-library";
import { CLIENT_ID } from "../consts";
import pool from "../utils/db";
import {
    decryptAesGcm,
    deriveKeyScryptCached,
    encryptAesGcm,
    getApplicationKey,
    hmacSha256,
} from "../utils/encrypt";

const oAuth2Client = new OAuth2Client();

export class User {
    id?: number;
    encryptionKey: Buffer;

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
        encryptionKey: Buffer,
        email: string,
        odooUrl?: string,
        odooToken?: string,
        loginToken?: string,
        loginTokenExpireAt?: Date,
        translations?: any,
        translationsExpireAt?: Date,
    ) {
        this.id = id;
        this.encryptionKey = encryptionKey;
        this.email = email;
        this.odooUrl = odooUrl;
        this.odooToken = odooToken;
        this.loginToken = loginToken;
        this.loginTokenExpireAt = loginTokenExpireAt;
        this.translations = translations;
        this.translationsExpireAt = translationsExpireAt;
    }

    async save() {
        console.log(`Saving user ${this.email}`);

        const enc = (pt) => encryptAesGcm(pt, this.encryptionKey);
        await pool.query(
            `
                INSERT INTO enc_users_settings (
                                key_hash,
                                enc_odoo_url,
                                enc_odoo_token,
                                enc_login_token,
                                login_token_expire_at,
                                enc_translations,
                                enc_translations_expire_at
                            )
                     VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (key_hash) DO UPDATE
                        SET
                            enc_odoo_url = EXCLUDED.enc_odoo_url,
                            enc_odoo_token = EXCLUDED.enc_odoo_token,
                            enc_login_token = EXCLUDED.enc_login_token,
                            login_token_expire_at = EXCLUDED.login_token_expire_at,
                            enc_translations = EXCLUDED.enc_translations,
                            enc_translations_expire_at = EXCLUDED.enc_translations_expire_at
            `,
            [
                // don't use a salt per user because it's used to get the user's SQL row
                // (should be impossible to guess without the application secret)
                hmacSha256(this.encryptionKey, "Hash Key Salt"),
                enc(this.odooUrl),
                enc(this.odooToken),
                enc(this.loginToken),
                this.loginTokenExpireAt?.toISOString(),
                enc(JSON.stringify(this.translations)),
                enc(this.translationsExpireAt?.toISOString()),
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
        const decodedToken = await oAuth2Client.verifyIdToken({
            idToken: event.authorizationEventObject.userIdToken,
            audience: CLIENT_ID,
        });
        const payload = decodedToken.getPayload();
        if (!payload.email || !payload.email_verified) {
            throw new Error("Failed to authenticate the user");
        }

        // Derive the user key from the application secret, the sub from the Google token
        // (70 bits) and the email of the user to add more entropy. The goal is to mitigate
        // the damage in case of a database leak (one will need to get the application secret
        // we used, and the email / sub token for each user). We don't use a salt per user
        // because we will use the hash of the key to get the record from the database,
        // with a salt we will need to fetch all salts in the database to find one that match).
        const userSub = `${payload.sub}-${payload.email.toLowerCase()}`;
        const userKeySeed = hmacSha256(await getApplicationKey(), userSub).toString("hex");
        const encryptionKey = await deriveKeyScryptCached(userKeySeed, "Odoo-Gmail-Addin-Salt");
        return await User._getUserFromEncryptionKey(encryptionKey, payload.email);
    }

    /**
     * Check the token we receive from the user's browser, and get the user.
     *
     * The login token can only be used once, and is reset after getting the user.
     */
    static async getUserFromLoginToken(
        email: string,
        encryptionKey: Buffer,
        loginToken: string,
    ): Promise<User> {
        const user = await User._getUserFromEncryptionKey(encryptionKey, email);

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

    private static async _getUserFromEncryptionKey(
        encryptionKey: Buffer,
        email: string,
    ): Promise<User> {
        const keyHash = hmacSha256(encryptionKey, "Hash Key Salt");
        const result = await pool.query(
            `
                SELECT id,
                       enc_odoo_url,
                       enc_odoo_token,
                       enc_login_token,
                       login_token_expire_at,
                       enc_translations,
                       enc_translations_expire_at
                  FROM enc_users_settings
                 WHERE key_hash = $1
            `,
            [keyHash],
        );
        if (result.rows.length === 0) {
            // new user
            return new User(null, encryptionKey, email);
        }

        try {
            const dec = (ct) => decryptAesGcm(ct, encryptionKey);
            const data = result.rows[0];
            return new User(
                data.id,
                encryptionKey,
                email,
                dec(data.enc_odoo_url),
                dec(data.enc_odoo_token),
                dec(data.enc_login_token),
                data.login_token_expire_at && new Date(data.login_token_expire_at),
                data.enc_translations && JSON.parse(dec(data.enc_translations)),
                data.enc_translations_expire_at && new Date(dec(data.enc_translations_expire_at)),
            );
        } catch (error) {
            console.log(`Decryption failed for ${email}, ${error}`);
            return new User(null, encryptionKey, email);
        }
    }
}
