"""Provider-agnostic transactional email service for Qapilo.

Currently backed by Emergent's managed email proxy (Resend). The rest of the app
only calls `send_and_log(...)` / the template helpers, so the provider can be
swapped by changing `_provider_send` alone. NO marketing email lives here.
"""
import os
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)

# Emergent managed email proxy — this base URL is a CONSTANT (survives deploy).
EMAIL_BASE_URL = "https://integrations.emergentagent.com"
EMAIL_KEY = os.environ.get("EMERGENT_EMAIL_KEY", "")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Qapilo")
SUPPORT_EMAIL = os.environ.get("QAPILO_SUPPORT_EMAIL", "").strip()  # owner-provided; may be empty

SUPPORTED_LANGS = ("en", "de", "es")


def _lang(lang: str) -> str:
    return lang if lang in SUPPORTED_LANGS else "en"


async def _provider_send(to: str, subject: str, html: str, reply_to: str | None = None) -> str:
    """Send one email through the managed proxy. Returns provider message id.
    Raises on failure so the caller can record a failed delivery event."""
    if not EMAIL_KEY:
        raise RuntimeError("email_key_missing")
    payload = {"to": [to], "subject": subject, "html": html, "from_name": EMAIL_FROM_NAME}
    if reply_to:
        payload["contact_email"] = reply_to
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{EMAIL_BASE_URL}/api/v1/email/send",
            headers={"X-Email-Key": EMAIL_KEY},
            json=payload,
        )
    resp.raise_for_status()
    try:
        return resp.json().get("id", "")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Templates (EN / DE / ES). Each returns (subject, list_of_paragraphs, button|None)
# Button = (label, url) or None. Kept neutral, educational, no marketing.
# ---------------------------------------------------------------------------
_T = {
    "email_verification": {
        "en": {
            "subject": "Confirm your Qapilo email",
            "p": [
                "Welcome to Qapilo! Please confirm your email address to secure your account.",
                "Enter this 6-digit code in the app: {code}",
                "This code expires in {ttl} minutes. If you didn't create a Qapilo account, you can ignore this email.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Bestätige deine Qapilo-E-Mail",
            "p": [
                "Willkommen bei Qapilo! Bitte bestätige deine E-Mail-Adresse, um dein Konto abzusichern.",
                "Gib diesen 6-stelligen Code in der App ein: {code}",
                "Dieser Code läuft in {ttl} Minuten ab. Falls du kein Qapilo-Konto erstellt hast, kannst du diese E-Mail ignorieren.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Confirma tu correo de Qapilo",
            "p": [
                "¡Bienvenido a Qapilo! Confirma tu dirección de correo para proteger tu cuenta.",
                "Introduce este código de 6 dígitos en la app: {code}",
                "Este código caduca en {ttl} minutos. Si no creaste una cuenta de Qapilo, puedes ignorar este correo.",
            ],
            "btn": None,
        },
    },
    "marketing_confirmation": {
        "en": {
            "subject": "Confirm your Qapilo marketing emails",
            "p": [
                "You asked to receive occasional marketing emails and newsletters from Qapilo. This confirms that request (double opt-in) — no marketing has been sent yet.",
                "Enter this 6-digit code in the app: {code}",
                "This code expires in {ttl} minutes. If you didn't request this, you can ignore this email and no marketing emails will be sent.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Bestätige deine Qapilo-Marketing-E-Mails",
            "p": [
                "Du hast darum gebeten, gelegentlich Marketing-E-Mails und Newsletter von Qapilo zu erhalten. Dies bestätigt diese Anfrage (Double-Opt-in) — es wurde noch kein Marketing versendet.",
                "Gib diesen 6-stelligen Code in der App ein: {code}",
                "Dieser Code läuft in {ttl} Minuten ab. Falls du das nicht angefordert hast, kannst du diese E-Mail ignorieren — es werden keine Marketing-E-Mails versendet.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Confirma tus correos de marketing de Qapilo",
            "p": [
                "Pediste recibir correos de marketing y boletines ocasionales de Qapilo. Esto confirma esa solicitud (doble consentimiento) — todavía no se ha enviado ningún correo de marketing.",
                "Introduce este código de 6 dígitos en la app: {code}",
                "Este código caduca en {ttl} minutos. Si no solicitaste esto, puedes ignorar este correo: no se enviará ningún correo de marketing.",
            ],
            "btn": None,
        },
    },
    "password_reset": {
        "en": {
            "subject": "Reset your Qapilo password",
            "p": [
                "We received a request to reset the password for your Qapilo account.",
                "Use the button below to choose a new password. This link expires in {ttl} minutes and can be used once.",
                "If you didn't request this, you can safely ignore this email — your password stays unchanged.",
            ],
            "btn": ("Reset password", "{link}"),
            "code_note": "Or enter this code in the app: {token}",
        },
        "de": {
            "subject": "Setze dein Qapilo-Passwort zurück",
            "p": [
                "Wir haben eine Anfrage erhalten, das Passwort deines Qapilo-Kontos zurückzusetzen.",
                "Wähle über die Schaltfläche unten ein neues Passwort. Dieser Link läuft in {ttl} Minuten ab und ist einmalig gültig.",
                "Falls du das nicht warst, kannst du diese E-Mail ignorieren — dein Passwort bleibt unverändert.",
            ],
            "btn": ("Passwort zurücksetzen", "{link}"),
            "code_note": "Oder gib diesen Code in der App ein: {token}",
        },
        "es": {
            "subject": "Restablece tu contraseña de Qapilo",
            "p": [
                "Recibimos una solicitud para restablecer la contraseña de tu cuenta de Qapilo.",
                "Usa el botón de abajo para elegir una nueva contraseña. Este enlace caduca en {ttl} minutos y solo se puede usar una vez.",
                "Si no lo solicitaste, puedes ignorar este correo con seguridad; tu contraseña no cambiará.",
            ],
            "btn": ("Restablecer contraseña", "{link}"),
            "code_note": "O introduce este código en la app: {token}",
        },
    },
    "account_deleted": {
        "en": {
            "subject": "Your Qapilo account has been deleted",
            "p": [
                "Your Qapilo account and associated learning data have been permanently deleted.",
                "If you had a subscription purchased through PayPal, Apple or Google, please also verify its cancellation in that provider's account.",
                "We're sorry to see you go. You're welcome back anytime.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Dein Qapilo-Konto wurde gelöscht",
            "p": [
                "Dein Qapilo-Konto und die zugehörigen Lerndaten wurden dauerhaft gelöscht.",
                "Falls du ein Abo über PayPal, Apple oder Google hattest, prüfe die Kündigung bitte zusätzlich im Konto des jeweiligen Anbieters.",
                "Schade, dass du gehst. Du bist jederzeit wieder willkommen.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Tu cuenta de Qapilo ha sido eliminada",
            "p": [
                "Tu cuenta de Qapilo y los datos de aprendizaje asociados se han eliminado de forma permanente.",
                "Si tenías una suscripción comprada a través de PayPal, Apple o Google, verifica también su cancelación en la cuenta de ese proveedor.",
                "Lamentamos que te vayas. Puedes volver cuando quieras.",
            ],
            "btn": None,
        },
    },
    "support_received": {
        "en": {
            "subject": "We received your Qapilo support request",
            "p": [
                "Thanks for reaching out. We received your support request and will get back to you as soon as possible.",
                "Your reference: {ref}\nCategory: {category}\nSubject: {subj}",
                "Please don't share passwords or payment details in support messages.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Wir haben deine Qapilo-Supportanfrage erhalten",
            "p": [
                "Danke für deine Nachricht. Wir haben deine Supportanfrage erhalten und melden uns so schnell wie möglich.",
                "Deine Referenz: {ref}\nKategorie: {category}\nBetreff: {subj}",
                "Bitte teile in Supportnachrichten keine Passwörter oder Zahlungsdaten.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Hemos recibido tu solicitud de soporte de Qapilo",
            "p": [
                "Gracias por escribirnos. Hemos recibido tu solicitud de soporte y te responderemos lo antes posible.",
                "Tu referencia: {ref}\nCategoría: {category}\nAsunto: {subj}",
                "Por favor, no compartas contraseñas ni datos de pago en los mensajes de soporte.",
            ],
            "btn": None,
        },
    },
    "support_forwarded": {
        "en": {
            "subject": "[Support {ref}] {subj}",
            "p": [
                "New support request via Qapilo.",
                "Reference: {ref}\nCategory: {category}\nFrom: {frm}\nLanguage: {lng}",
                "Message:\n{msg}",
            ],
            "btn": None,
        },
        "de": {
            "subject": "[Support {ref}] {subj}",
            "p": [
                "Neue Supportanfrage über Qapilo.",
                "Referenz: {ref}\nKategorie: {category}\nVon: {frm}\nSprache: {lng}",
                "Nachricht:\n{msg}",
            ],
            "btn": None,
        },
        "es": {
            "subject": "[Support {ref}] {subj}",
            "p": [
                "Nueva solicitud de soporte vía Qapilo.",
                "Referencia: {ref}\nCategoría: {category}\nDe: {frm}\nIdioma: {lng}",
                "Mensaje:\n{msg}",
            ],
            "btn": None,
        },
    },
    "subscription_activated": {
        "en": {
            "subject": "Your Qapilo Pro subscription is active",
            "p": [
                "Your Qapilo Pro subscription is now active. You have full access to the AI Tutor and advanced lessons.",
                "This is a Qapilo service confirmation, not a payment receipt. Your official receipt is issued by PayPal.",
                "You can manage or cancel your subscription anytime in Settings or in your PayPal account.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Dein Qapilo-Pro-Abo ist aktiv",
            "p": [
                "Dein Qapilo-Pro-Abo ist jetzt aktiv. Du hast vollen Zugriff auf den KI-Tutor und die erweiterten Lektionen.",
                "Dies ist eine Qapilo-Servicebestätigung, kein Zahlungsbeleg. Deinen offiziellen Beleg stellt PayPal aus.",
                "Du kannst dein Abo jederzeit in den Einstellungen oder in deinem PayPal-Konto verwalten oder kündigen.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Tu suscripción Qapilo Pro está activa",
            "p": [
                "Tu suscripción Qapilo Pro ya está activa. Tienes acceso completo al Tutor IA y a las lecciones avanzadas.",
                "Esta es una confirmación de servicio de Qapilo, no un recibo de pago. Tu recibo oficial lo emite PayPal.",
                "Puedes gestionar o cancelar tu suscripción cuando quieras en Ajustes o en tu cuenta de PayPal.",
            ],
            "btn": None,
        },
    },
    "subscription_cancelled": {
        "en": {
            "subject": "Your Qapilo Pro subscription was cancelled",
            "p": [
                "Your Qapilo Pro subscription has been cancelled. You can keep using the free features anytime.",
                "This is a Qapilo service confirmation, not a payment document. Any billing is handled by PayPal.",
                "If you didn't request this cancellation, please contact support.",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Dein Qapilo-Pro-Abo wurde gekündigt",
            "p": [
                "Dein Qapilo-Pro-Abo wurde gekündigt. Du kannst die kostenlosen Funktionen weiterhin nutzen.",
                "Dies ist eine Qapilo-Servicebestätigung, kein Zahlungsdokument. Die Abrechnung erfolgt über PayPal.",
                "Falls du diese Kündigung nicht veranlasst hast, kontaktiere bitte den Support.",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Tu suscripción Qapilo Pro fue cancelada",
            "p": [
                "Tu suscripción Qapilo Pro ha sido cancelada. Puedes seguir usando las funciones gratuitas cuando quieras.",
                "Esta es una confirmación de servicio de Qapilo, no un documento de pago. La facturación la gestiona PayPal.",
                "Si no solicitaste esta cancelación, ponte en contacto con soporte.",
            ],
            "btn": None,
        },
    },
    "trial_started": {
        "en": {
            "subject": "Welcome to Qapilo — your free trial has started",
            "p": [
                "Welcome to Qapilo! Your {days}-day free trial has started, so you can explore the AI Tutor and lessons.",
                "Qapilo is a financial education platform. Everything here is for learning only and is not financial or investment advice.",
                "Happy learning!",
            ],
            "btn": None,
        },
        "de": {
            "subject": "Willkommen bei Qapilo — deine kostenlose Testphase hat begonnen",
            "p": [
                "Willkommen bei Qapilo! Deine {days}-tägige kostenlose Testphase hat begonnen — entdecke den KI-Tutor und die Lektionen.",
                "Qapilo ist eine Plattform für Finanzbildung. Alle Inhalte dienen ausschließlich dem Lernen und sind keine Finanz- oder Anlageberatung.",
                "Viel Freude beim Lernen!",
            ],
            "btn": None,
        },
        "es": {
            "subject": "Bienvenido a Qapilo: tu prueba gratuita ha comenzado",
            "p": [
                "¡Bienvenido a Qapilo! Tu prueba gratuita de {days} días ha comenzado; explora el Tutor IA y las lecciones.",
                "Qapilo es una plataforma de educación financiera. Todo el contenido es solo para aprender y no constituye asesoramiento financiero ni de inversión.",
                "¡Feliz aprendizaje!",
            ],
            "btn": None,
        },
    },
}

_FOOTER = {
    "en": "You received this email because of activity on your Qapilo account.",
    "de": "Du erhältst diese E-Mail aufgrund von Aktivität in deinem Qapilo-Konto.",
    "es": "Recibes este correo por actividad en tu cuenta de Qapilo.",
}


def _wrap(subject: str, paragraphs: list[str], button, footer: str) -> str:
    body = ""
    for p in paragraphs:
        safe = p.replace("\n", "<br/>")
        body += (
            f'<tr><td style="padding:0 0 16px 0;font-size:15px;line-height:22px;'
            f'color:#1f2937;">{safe}</td></tr>'
        )
    if button:
        label, url = button
        body += (
            f'<tr><td style="padding:8px 0 20px 0;"><a href="{url}" '
            f'style="display:inline-block;background:#0F9D58;color:#ffffff;'
            f'text-decoration:none;font-weight:600;padding:12px 22px;border-radius:8px;'
            f'font-size:15px;">{label}</a></td></tr>'
        )
    support = ""
    if SUPPORT_EMAIL:
        support = (f'<br/>{footer.split(".")[0]}. Support: '
                   f'<a href="mailto:{SUPPORT_EMAIL}" style="color:#0F9D58;">{SUPPORT_EMAIL}</a>')
    return (
        '<!doctype html><html><body style="margin:0;padding:0;background:#f3f4f6;">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="background:#f3f4f6;padding:24px 0;"><tr><td align="center">'
        '<table role="presentation" width="480" cellpadding="0" cellspacing="0" '
        'style="background:#ffffff;border-radius:12px;padding:28px;max-width:480px;'
        'font-family:Arial,Helvetica,sans-serif;">'
        '<tr><td style="padding:0 0 18px 0;font-size:22px;font-weight:700;color:#0F9D58;">Qapilo</td></tr>'
        f'<tr><td style="padding:0 0 16px 0;font-size:18px;font-weight:700;color:#111827;">{subject}</td></tr>'
        f'{body}'
        f'<tr><td style="padding:16px 0 0 0;border-top:1px solid #e5e7eb;font-size:12px;'
        f'line-height:18px;color:#6b7280;">{footer}{support}</td></tr>'
        '</table></td></tr></table></body></html>'
    )


def render(template: str, lang: str, ctx: dict | None = None) -> tuple[str, str]:
    """Return (subject, html) for a template in the given language."""
    lang = _lang(lang)
    ctx = ctx or {}
    t = _T[template][lang]
    subject = t["subject"].format(**ctx)
    paras = [p.format(**ctx) for p in t["p"]]
    if template == "password_reset" and not ctx.get("link"):
        # No hosted app URL configured: show a copyable code instead of a link button.
        paras.append(t["code_note"].format(**ctx))
        button = None
    else:
        btn = t.get("btn")
        button = (btn[0], btn[1].format(**ctx)) if btn else None
    html = _wrap(subject, paras, button, _FOOTER[lang])
    return subject, html


async def send_and_log(db, template: str, lang: str, to: str, user_ref: str | None,
                       ctx: dict | None = None, reply_to: str | None = None) -> dict:
    """Render + send + record a MINIMAL delivery event. Never raises: returns
    a status dict so callers can fire-and-forget without breaking the request.
    Never stores email bodies, reset links or tokens."""
    lang = _lang(lang)
    event = {
        "event_id": f"em_{uuid.uuid4().hex[:16]}",
        "template": template,
        "user_ref": user_ref,          # user_id, never the raw email
        "provider_message_id": None,
        "status": "pending",
        "language": lang,
        "created_at": datetime.now(timezone.utc),
        "last_attempt_at": datetime.now(timezone.utc),
        "failure_category": None,
    }
    try:
        subject, html = render(template, lang, ctx)
        msg_id = await _provider_send(to, subject, html, reply_to=reply_to)
        event["status"] = "sent"
        event["provider_message_id"] = msg_id or None
    except httpx.HTTPStatusError as e:
        event["status"] = "failed"
        event["failure_category"] = f"http_{e.response.status_code}"
        logger.error(f"email {template} failed: http {e.response.status_code}")
    except Exception as e:
        event["status"] = "failed"
        event["failure_category"] = type(e).__name__
        logger.error(f"email {template} failed: {type(e).__name__}")
    try:
        await db.email_events.insert_one(event)
    except Exception:
        logger.warning("could not write email_event log")
    return {"status": event["status"], "event_id": event["event_id"]}
