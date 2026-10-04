"""Adaptador de salida: cifrado de contraseñas con werkzeug (scrypt / pbkdf2 con sal)."""

from werkzeug.security import check_password_hash, generate_password_hash


class WerkzeugPasswordHasher:
    def hashear(self, password: str) -> str:
        return generate_password_hash(password)

    def verificar(self, password_hash: str, password: str) -> bool:
        return check_password_hash(password_hash, password)
