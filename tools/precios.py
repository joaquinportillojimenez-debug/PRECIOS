#!/usr/bin/env python3
"""Cifra / descifra los datos de la web de precios.

Los datos en claro (ventas.json) NUNCA se suben al repositorio: solo se sube
data.enc.json, cifrado con AES-GCM y una clave derivada de la contraseña con
PBKDF2-SHA256. La web descifra en el navegador con WebCrypto.

Cada entrada de "sales" es una venta cerrada, o una venta esperada si lleva
"kind": "esperada" (lo que espera sacarle quien acaba de comprarlo, con "buy"
= lo que pagó); las esperadas no cuentan para la mediana de venta.

Uso:
  PRECIOS_PASS='...' python3 tools/precios.py check   ventas.json
  PRECIOS_PASS='...' python3 tools/precios.py encrypt ventas.json data.enc.json
  PRECIOS_PASS='...' python3 tools/precios.py decrypt data.enc.json ventas.json

Al cifrar se reutiliza la sal del data.enc.json existente (si lo hay), para que
la clave que el iPad tiene guardada siga valiendo tras cada actualización.
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 310_000


def b64e(b):
    return base64.b64encode(b).decode()


def b64d(s):
    return base64.b64decode(s)


def password():
    pw = os.environ.get("PRECIOS_PASS")
    if not pw:
        sys.exit("Falta la contraseña en PRECIOS_PASS")
    return pw.encode("utf-8")


def derive(pw, salt, it):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw)


def check(data):
    cats = {c["id"] for c in data["cats"]}
    prods = {}
    for p in data["products"]:
        assert p["id"] not in prods, f"producto repetido: {p['id']}"
        assert p["cat"] in cats, f"categoría desconocida en {p['id']}: {p['cat']}"
        prods[p["id"]] = p
    used = set()
    for i, s in enumerate(data["sales"]):
        assert s["p"] in prods, f"venta {i}: producto desconocido {s['p']}"
        assert isinstance(s["price"], (int, float)) and s["price"] > 0, f"venta {i}: precio raro"
        assert s.get("kind", "venta") in ("venta", "esperada"), f"venta {i}: tipo raro {s.get('kind')}"
        used.add(s["p"])
    unused = [p for p in prods if p not in used]
    print(f"OK: {len(data['cats'])} categorías, {len(prods)} productos, {len(data['sales'])} ventas")
    if unused:
        print("Productos sin ventas:", ", ".join(unused))


def encrypt(src, dst):
    data = json.load(open(src, encoding="utf-8"))
    check(data)
    salt = None
    if os.path.exists(dst):
        try:
            salt = b64d(json.load(open(dst))["salt"])
        except Exception:
            salt = None
    salt = salt or os.urandom(16)
    key = derive(password(), salt, ITER)
    iv = os.urandom(12)
    plain = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ct = AESGCM(key).encrypt(iv, plain, None)
    out = {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b64e(salt), "iv": b64e(iv), "ct": b64e(ct)}
    with open(dst, "w") as f:
        json.dump(out, f)
        f.write("\n")
    print(f"Cifrado -> {dst} ({len(ct)} bytes)")


def decrypt(src, dst):
    env = json.load(open(src))
    key = derive(password(), b64d(env["salt"]), env["iter"])
    plain = AESGCM(key).decrypt(b64d(env["iv"]), b64d(env["ct"]), None)
    data = json.loads(plain)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Descifrado -> {dst}")
    check(data)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "check":
        check(json.load(open(sys.argv[2], encoding="utf-8")))
    elif cmd == "encrypt":
        encrypt(sys.argv[2], sys.argv[3])
    elif cmd == "decrypt":
        decrypt(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
