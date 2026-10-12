import test from "node:test";
import assert from "node:assert/strict";
import { randomBytes } from "node:crypto";
import { performance } from "node:perf_hooks";
import {
  encryptAesGcm,
  decryptAesGcm,
  deriveKeyScrypt,
  deriveKeyScryptCached,
} from "../src/utils/encrypt";

function randomString(n: number): string {
  return randomBytes(n).toString("base64url").slice(0, n);
}

test("decrypt(encrypt(x))", () => {
  assert.deepEqual(encryptAesGcm(undefined, randomBytes(32)), undefined);
  for (let size = 1; size < 1000; ++size) {
    const key = randomBytes(32);
    const original = randomString(size);
    const encrypted = encryptAesGcm(original, key);
    assert.equal(encrypted?.length, 12 + 16 + size); // GCM is stream cipher
    const decrypted = decryptAesGcm(encrypted, key);
    assert.equal(decrypted, original);
    assert.ok(Buffer.isBuffer(encrypted));
  }
});

test("check that the IV change", () => {
  const key = randomBytes(32);
  const first = encryptAesGcm("plaintext", key);
  const second = encryptAesGcm("plaintext", key);
  assert.notDeepEqual(first, second);
});

test("wrong key raises", () => {
  const goodKey = randomBytes(32);
  const badKey = randomBytes(32);
  const encrypted = encryptAesGcm("plaintext", goodKey);
  assert.equal(decryptAesGcm(encrypted, goodKey), "plaintext");
  assert.throws(() => decryptAesGcm(encrypted, badKey));
});

test("raise when altering iv - tag - ct", () => {
  const key = randomBytes(32);
  const encrypted = encryptAesGcm("plaintext plaintext plaintext", key);
  assert.ok(encrypted);

  // [IV: 12][tag: 16][ciphertext]
  const modifiedIv = Buffer.from(encrypted);
  modifiedIv[3] ^= 0xff;
  assert.throws(() => decryptAesGcm(modifiedIv, key));

  const modifiedTag = Buffer.from(encrypted);
  modifiedTag[17] ^= 0xff;
  assert.throws(() => decryptAesGcm(modifiedTag, key));

  // pt block 1
  const modifiedCt1 = Buffer.from(encrypted);
  modifiedCt1[40] ^= 0xff;
  assert.throws(() => decryptAesGcm(modifiedCt1, key));

  // pt block 2
  const modifiedCt2 = Buffer.from(encrypted);
  modifiedCt2[55] ^= 0xff;
  assert.throws(() => decryptAesGcm(modifiedCt2, key));
});

test("raise when wrong size", () => {
  const key = randomBytes(32);
  const encrypted = encryptAesGcm("plaintext", key);
  assert.ok(encrypted);
  assert.throws(() => decryptAesGcm(encrypted.subarray(0, 0), key));
  assert.throws(() => decryptAesGcm(encrypted.subarray(0, 2), key));
});

test("derives the same password with the same salt", async () => {
  const startedAt = performance.now();
  const key1 = await deriveKeyScrypt("password", "salt");
  const durationMs = performance.now() - startedAt;
  console.log(`scrypt took ${durationMs.toFixed(2)} ms`); // ~50ms on laptop
  const key2 = await deriveKeyScrypt("password", "salt");
  assert.equal(key1.length, 32);
  assert.deepEqual(key1, key2);
});

test("derives different password with the same salt", async () => {
  const key1 = await deriveKeyScrypt("password 1", "salt");
  const key2 = await deriveKeyScrypt("password 2", "salt");
  assert.equal(key1.length, 32);
  assert.equal(key2.length, 32);
  assert.notDeepEqual(key1, key2);
});


test("derives with no salt raises", async () => {
  await assert.rejects(() => deriveKeyScrypt("password 2", ""));
});


test("deriveKeyScryptCached", async () => {
  const password = randomString(64);
  // first generation is slow
  const startedAt1 = performance.now();
  const key1 = await deriveKeyScryptCached(password, "salt");
  const time1 = performance.now() - startedAt1;

  // second hit the cache
  const startedAt2 = performance.now();
  const key2 = await deriveKeyScryptCached(password, "salt");
  const time2 = performance.now() - startedAt2;

  assert.deepEqual(key1, key2);
  assert.ok(time1 > time2);
  assert.ok(time1 > time2 + 10);
});
