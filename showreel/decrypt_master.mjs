import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const ROOT = process.cwd();
const ENC_IN = process.env.ENC_IN || path.join(ROOT, 'deliverables', 'MON-DEMO26_v3_Master_60fps.enc');
const KEY_PATH = process.argv[2] || '/tmp/monarch_master_rsa.pem';
const OUT_MP4 = process.env.OUT_MP4 || path.join(ROOT, 'deliverables', 'MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4');

const packet = fs.readFileSync(ENC_IN);
const privPem = fs.readFileSync(KEY_PATH, 'utf8');

const wrappedLen = packet.readUInt32BE(0);
let off = 4;
const wrappedKey = packet.subarray(off, off + wrappedLen);
off += wrappedLen;
const iv = packet.subarray(off, off + 12);
off += 12;
const authTag = packet.subarray(off, off + 16);
off += 16;
const ciphertext = packet.subarray(off);

const aesKey = crypto.privateDecrypt(
  {
    key: privPem,
    padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
    oaepHash: 'sha256',
  },
  wrappedKey
);

const decipher = crypto.createDecipheriv('aes-256-gcm', aesKey, iv);
decipher.setAuthTag(authTag);
const plain = Buffer.concat([decipher.update(ciphertext), decipher.final()]);

fs.mkdirSync(path.dirname(OUT_MP4), { recursive: true });
fs.writeFileSync(OUT_MP4, plain);
console.log(`Decrypted ${OUT_MP4} (${(plain.length / (1024 * 1024)).toFixed(2)} MB)`);
