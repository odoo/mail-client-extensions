import {
    createCipheriv,
    createDecipheriv,
    createHash,
    createHmac,
    randomBytes,
    scrypt,
    ScryptOptions,
} from "node:crypto";
import { promisify } from "node:util";

/**
 * Encrypt in AES 256 GCM the given plaintext.
 *
 * Use AES 256 GCM because it prevents ciphertext from being malleable
 * (it's authenticated), tag length of 16 bytes (which is the default).
 * IV is 12 and not 16 bytes for GCM because of the counter.
 *
 * We also wanted something builtin to avoid adding dependencies
 * (and GCM is the only one that provide authenticity, compared to CBC
 * / CTR for which we would need to implement it ourselves).
 */
export function encryptAesGcm(
    plaintext: string | Buffer | undefined,
    key: Buffer,
): Buffer | undefined {
    if (!plaintext) {
        // for simplicity, don't encrypt undefined value
        return;
    }
    if (key.length !== 32) {
        throw new TypeError("Invalid key");
    }

    const iv = randomBytes(12);
    const cipher = createCipheriv("aes-256-gcm", key, iv, { authTagLength: 16 });
    const ciphertext = cipher.update(plaintext);
    cipher.final();
    const tag = cipher.getAuthTag();
    return Buffer.concat([iv, tag, ciphertext]);
}

/**
 * Decrypt in AES 256 GCM the given payload.
 */
export function decryptAesGcm(
    ivTagCiphertextBlob: Buffer | undefined,
    key: Buffer,
): string | undefined {
    if (!ivTagCiphertextBlob) {
        // for simplicity, don't encrypt undefined value
        return;
    }
    if (ivTagCiphertextBlob.length < 12 + 16) {
        throw new Error("Invalid ciphertext");
    }
    const iv = ivTagCiphertextBlob.subarray(0, 12);
    const tag = ivTagCiphertextBlob.subarray(12, 12 + 16);
    const ciphertext = ivTagCiphertextBlob.subarray(12 + 16);
    const decipher = createDecipheriv("aes-256-gcm", key, iv, { authTagLength: 16 });
    decipher.setAuthTag(tag);
    const plaintext = decipher.update(ciphertext);
    decipher.final(); // check tag
    return plaintext.toString();
}

const _scryptAsync = promisify(scrypt) as (
    password: string,
    salt: string,
    keylen: number,
    options: ScryptOptions,
) => Promise<Buffer>;

/**
 * Derive a 256 bits key from the given seed with scrypt.
 *
 * We use scrypt because it's memory expensive compare to PBKDF2 or HKDF.
 * We don't use Argon2 because it's only available on newer node version.
 */
export async function deriveKeyScrypt(seed: string, salt: string): Promise<Buffer> {
    if (!seed.length || !salt.length) {
        throw new TypeError("Invalid seed");
    }
    // Use 64MB of maximum memory instead of the default 32,
    // and 2**15 rounds instead of the default 2**14
    const options = {
        N: 2 ** 15,
        r: 8,
        p: 1,
        maxmem: 64 * 1024 * 1024,
    };
    // 32 bytes for the AES key
    return _scryptAsync(seed, salt, 32, options);
}

const KEY_CACHE_MAX_SIZE = 10000;
const _derivedKeyCache = new Map<string, Buffer>();

/**
 * Handwritten LRU cache to avoid adding dependencies.
 */
export async function deriveKeyScryptCached(seed: string, salt: string): Promise<Buffer> {
    const cacheKey = createHash("sha256").update(`${salt}-${seed}`).digest("hex");
    const cached = _derivedKeyCache.get(cacheKey);
    if (cached) {
        // refresh LRU order
        _derivedKeyCache.delete(cacheKey);
        _derivedKeyCache.set(cacheKey, cached);
        return cached;
    }

    const key = await deriveKeyScrypt(seed, salt);
    if (_derivedKeyCache.size >= KEY_CACHE_MAX_SIZE) {
        // remove the oldest entry
        _derivedKeyCache.delete(_derivedKeyCache.keys().next().value);
    }
    _derivedKeyCache.set(cacheKey, key);
    return key;
}

export function hmacSha256(key: Buffer | string, data: string): Buffer {
    return createHmac("sha256", key).update(data).digest();
}

/**
 * Derive the application key from the application secret.
 */
export async function getApplicationKey(): Promise<Buffer> {
    if (!process.env.APP_SECRET?.length) {
        throw new Error("Application secret not configured");
    }
    return deriveKeyScryptCached(process.env.APP_SECRET, "APPLICATION KEY");
}
