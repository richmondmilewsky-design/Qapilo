"""Localized API error messages (EN/DE/ES).

The active request language is stored in a contextvar set by a lightweight
middleware that reads the Accept-Language header. L("code") returns the message
in the current request language, falling back to English. This localizes only the
human-readable error text — status codes and business logic are unchanged.
"""
import contextvars

lang_ctx = contextvars.ContextVar("req_lang", default="en")

SUPPORTED = ("en", "de", "es")


def set_lang_from_header(accept_language: str):
    code = (accept_language or "").split(",")[0].strip().lower()[:2]
    lang_ctx.set(code if code in SUPPORTED else "en")


ERRORS = {
    "not_authenticated": {
        "en": "Not authenticated",
        "de": "Nicht authentifiziert",
        "es": "No autenticado",
    },
    "invalid_token": {
        "en": "Invalid or expired token",
        "de": "Ungültiges oder abgelaufenes Token",
        "es": "Token no válido o caducado",
    },
    "user_not_found": {
        "en": "User not found",
        "de": "Benutzer nicht gefunden",
        "es": "Usuario no encontrado",
    },
    "email_taken": {
        "en": "Email already registered",
        "de": "E-Mail ist bereits registriert",
        "es": "El correo ya está registrado",
    },
    "bad_credentials": {
        "en": "Invalid email or password",
        "de": "Ungültige E-Mail oder ungültiges Passwort",
        "es": "Correo o contraseña no válidos",
    },
    "google_invalid": {
        "en": "Google session invalid",
        "de": "Google-Sitzung ungültig",
        "es": "Sesión de Google no válida",
    },
    "apple_invalid": {
        "en": "Apple sign-in could not be verified",
        "de": "Apple-Anmeldung konnte nicht verifiziert werden",
        "es": "No se pudo verificar el inicio de sesión con Apple",
    },
    "reset_sent": {
        "en": "If an account exists for that email, we've sent password reset instructions.",
        "de": "Falls ein Konto mit dieser E-Mail existiert, haben wir eine Anleitung zum Zurücksetzen des Passworts gesendet.",
        "es": "Si existe una cuenta con ese correo, hemos enviado instrucciones para restablecer la contraseña.",
    },
    "reset_invalid": {
        "en": "This reset link is invalid or has expired.",
        "de": "Dieser Link zum Zurücksetzen ist ungültig oder abgelaufen.",
        "es": "Este enlace de restablecimiento no es válido o ha caducado.",
    },
    "verify_invalid": {
        "en": "This code is invalid or has expired.",
        "de": "Dieser Code ist ungültig oder abgelaufen.",
        "es": "Este código no es válido o ha caducado.",
    },
    "verify_sent": {
        "en": "We've sent a new confirmation code to your email.",
        "de": "Wir haben einen neuen Bestätigungscode an deine E-Mail gesendet.",
        "es": "Hemos enviado un nuevo código de confirmación a tu correo.",
    },
    "weak_password": {
        "en": "Password must be at least 8 characters.",
        "de": "Das Passwort muss mindestens 8 Zeichen lang sein.",
        "es": "La contraseña debe tener al menos 8 caracteres.",
    },
    "rate_limited": {
        "en": "Too many requests. Please try again later.",
        "de": "Zu viele Anfragen. Bitte versuche es später erneut.",
        "es": "Demasiadas solicitudes. Inténtalo de nuevo más tarde.",
    },
    "support_invalid": {
        "en": "Please fill in all required fields.",
        "de": "Bitte fülle alle erforderlichen Felder aus.",
        "es": "Por favor, completa todos los campos obligatorios.",
    },
    "reset_ok": {
        "en": "Your password has been updated. Please sign in again.",
        "de": "Dein Passwort wurde aktualisiert. Bitte melde dich erneut an.",
        "es": "Tu contraseña se ha actualizado. Vuelve a iniciar sesión.",
    },
    "support_ok": {
        "en": "Your support request was received.",
        "de": "Deine Supportanfrage wurde empfangen.",
        "es": "Tu solicitud de soporte fue recibida.",
    },
    "lesson_not_found": {
        "en": "Lesson not found",
        "de": "Lektion nicht gefunden",
        "es": "Lección no encontrada",
    },
    "lesson_pro": {
        "en": "This lesson requires Qapilo Pro",
        "de": "Diese Lektion erfordert Qapilo Pro",
        "es": "Esta lección requiere Qapilo Pro",
    },
    "stock_not_found": {
        "en": "Stock not found",
        "de": "Aktie nicht gefunden",
        "es": "Acción no encontrada",
    },
    "tutor_not_configured": {
        "en": "AI Tutor is not configured",
        "de": "Der KI-Tutor ist nicht konfiguriert",
        "es": "El Tutor IA no está configurado",
    },
    "message_empty": {
        "en": "Message is empty",
        "de": "Nachricht ist leer",
        "es": "El mensaje está vacío",
    },
    "tutor_limit": {
        "en": "You've used your free AI Tutor messages for today. Upgrade to Pro for unlimited chat.",
        "de": "Du hast deine kostenlosen KI-Tutor-Nachrichten für heute aufgebraucht. Upgrade auf Pro für unbegrenzten Chat.",
        "es": "Has usado tus mensajes gratuitos del Tutor IA de hoy. Pásate a Pro para chatear sin límites.",
    },
    "tutor_unavailable": {
        "en": "The AI Tutor is unavailable right now",
        "de": "Der KI-Tutor ist gerade nicht verfügbar",
        "es": "El Tutor IA no está disponible en este momento",
    },
    "paypal_auth_failed": {
        "en": "PayPal authentication failed",
        "de": "PayPal-Authentifizierung fehlgeschlagen",
        "es": "Error de autenticación de PayPal",
    },
    "paypal_product_failed": {
        "en": "Could not create PayPal product",
        "de": "PayPal-Produkt konnte nicht erstellt werden",
        "es": "No se pudo crear el producto de PayPal",
    },
    "paypal_plan_failed": {
        "en": "Could not create PayPal plan",
        "de": "PayPal-Plan konnte nicht erstellt werden",
        "es": "No se pudo crear el plan de PayPal",
    },
    "payments_not_configured": {
        "en": "Payments are not configured yet",
        "de": "Zahlungen sind noch nicht konfiguriert",
        "es": "Los pagos aún no están configurados",
    },
    "sub_start_failed": {
        "en": "Could not start subscription",
        "de": "Abo konnte nicht gestartet werden",
        "es": "No se pudo iniciar la suscripción",
    },
    "no_sub_to_activate": {
        "en": "No subscription to activate",
        "de": "Kein Abo zum Aktivieren vorhanden",
        "es": "No hay suscripción para activar",
    },
    "sub_verify_failed": {
        "en": "Could not verify subscription",
        "de": "Abo konnte nicht überprüft werden",
        "es": "No se pudo verificar la suscripción",
    },
    "consent_required": {
        "en": "You must accept the Terms of Service and the financial disclaimer to continue.",
        "de": "Du musst die Nutzungsbedingungen und den Finanzhinweis akzeptieren, um fortzufahren.",
        "es": "Debes aceptar los Términos de servicio y el aviso financiero para continuar.",
    },
}


def L(code: str) -> str:
    entry = ERRORS.get(code)
    if not entry:
        return code
    return entry.get(lang_ctx.get(), entry["en"])
