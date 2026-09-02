import type { Lang } from "@/src/i18n/translations";

type Section = { heading: string; body: string };
type Policy = { updated: string; intro: string; sections: Section[] };

const CONTACT = "privacy@qapilo.de";

const PRIVACY: Record<Lang, Policy> = {
  en: {
    updated: "Last updated: June 2026",
    intro:
      "Qapilo (\"we\", \"us\") respects your privacy. This policy explains what personal data we collect, why, and the rights you have under the EU General Data Protection Regulation (GDPR). Data controller: Qapilo.",
    sections: [
      {
        heading: "Data We Collect",
        body: "Account details (name, email, and a securely hashed password), your learning progress (XP, streaks, levels, badges, completed lessons, watchlist), your AI Tutor chat messages, your language preference, and — if you subscribe — your PayPal subscription ID and status. We never see or store your card details.",
      },
      {
        heading: "Why We Use It (Legal Basis)",
        body: "We process your data to provide the app and your account (performance of a contract), to remember your progress and preferences, and to operate the AI Tutor and subscriptions. Optional features rely on your consent, which you can withdraw at any time.",
      },
      {
        heading: "Third-Party Services",
        body: "To run the app we share the minimum necessary data with: Emergent (our application hosting/infrastructure provider, which also proxies AI Tutor messages to Anthropic's Claude model, sends transactional emails on our behalf, and handles parts of the Google sign-in session flow), PayPal (payment processing), Finnhub (live market data), Anthropic (AI Tutor responses), Tavily (news, only if enabled), and Google (only if you choose Google sign-in). Each processes data under its own privacy policy and, where required, a data processing agreement.",
      },
      {
        heading: "Data Retention",
        body: "We keep your data for as long as your account exists. When you delete your account, your profile and chat history are permanently removed from our systems.",
      },
      {
        heading: "Your Rights (GDPR)",
        body: "You have the right to access, correct, export, and delete your data, to object to or restrict processing, and to withdraw consent. You can export your data and delete your account at any time from Profile. You may also lodge a complaint with your local data protection authority.",
      },
      {
        heading: "Data Security",
        body: "Passwords are hashed, data is transmitted over encrypted connections, and access is restricted. No method of transmission is 100% secure, but we take reasonable measures to protect your information.",
      },
      {
        heading: "Children",
        body: "Qapilo is not directed at children under 16. We do not knowingly collect data from children. If you believe a child has provided us data, contact us and we will delete it.",
      },
      {
        heading: "Changes & Contact",
        body: `We may update this policy and will note the date above. For any privacy request or question, contact us at ${CONTACT}.`,
      },
    ],
  },
  de: {
    updated: "Zuletzt aktualisiert: Juni 2026",
    intro:
      "Qapilo („wir“) respektiert deine Privatsphäre. Diese Richtlinie erklärt, welche personenbezogenen Daten wir erheben, warum, und welche Rechte du nach der EU-Datenschutz-Grundverordnung (DSGVO) hast. Verantwortlicher: Qapilo.",
    sections: [
      {
        heading: "Welche Daten wir erheben",
        body: "Kontodaten (Name, E-Mail und ein sicher gehashtes Passwort), deinen Lernfortschritt (XP, Serien, Level, Abzeichen, abgeschlossene Lektionen, Merkliste), deine KI-Tutor-Nachrichten, deine Spracheinstellung und – falls du abonnierst – deine PayPal-Abo-ID und deren Status. Deine Kartendaten sehen und speichern wir nie.",
      },
      {
        heading: "Warum wir sie verwenden (Rechtsgrundlage)",
        body: "Wir verarbeiten deine Daten, um die App und dein Konto bereitzustellen (Vertragserfüllung), deinen Fortschritt und deine Einstellungen zu speichern sowie den KI-Tutor und Abos zu betreiben. Optionale Funktionen beruhen auf deiner Einwilligung, die du jederzeit widerrufen kannst.",
      },
      {
        heading: "Drittanbieter",
        body: "Zum Betrieb der App geben wir die minimal notwendigen Daten weiter an: Emergent (unser Hosting-/Infrastrukturanbieter, der außerdem KI-Tutor-Nachrichten an Anthropics Claude-Modell weiterleitet, transaktionale E-Mails in unserem Auftrag versendet und Teile des Google-Anmeldeprozesses abwickelt), PayPal (Zahlungsabwicklung), Finnhub (Live-Marktdaten), Anthropic (KI-Tutor-Antworten), Tavily (Nachrichten, nur falls aktiviert) und Google (nur bei Google-Anmeldung). Jeder verarbeitet Daten nach seiner eigenen Datenschutzrichtlinie und, soweit erforderlich, einem Auftragsverarbeitungsvertrag.",
      },
      {
        heading: "Speicherdauer",
        body: "Wir speichern deine Daten, solange dein Konto besteht. Wenn du dein Konto löschst, werden dein Profil und dein Chatverlauf dauerhaft aus unseren Systemen entfernt.",
      },
      {
        heading: "Deine Rechte (DSGVO)",
        body: "Du hast das Recht auf Auskunft, Berichtigung, Export und Löschung deiner Daten, auf Widerspruch oder Einschränkung der Verarbeitung sowie auf Widerruf der Einwilligung. Du kannst deine Daten jederzeit im Profil exportieren und dein Konto löschen. Du kannst dich auch bei deiner Datenschutzaufsichtsbehörde beschweren.",
      },
      {
        heading: "Datensicherheit",
        body: "Passwörter werden gehasht, Daten über verschlüsselte Verbindungen übertragen und der Zugriff ist beschränkt. Keine Übertragungsmethode ist zu 100 % sicher, aber wir treffen angemessene Maßnahmen zum Schutz deiner Daten.",
      },
      {
        heading: "Kinder",
        body: "Qapilo richtet sich nicht an Kinder unter 16 Jahren. Wir erheben wissentlich keine Daten von Kindern. Wenn du glaubst, dass ein Kind uns Daten übermittelt hat, kontaktiere uns und wir löschen sie.",
      },
      {
        heading: "Änderungen & Kontakt",
        body: `Wir können diese Richtlinie aktualisieren und vermerken das Datum oben. Für Datenschutzanfragen kontaktiere uns unter ${CONTACT}.`,
      },
    ],
  },
  es: {
    updated: "Última actualización: junio de 2026",
    intro:
      "Qapilo («nosotros») respeta tu privacidad. Esta política explica qué datos personales recopilamos, por qué, y los derechos que tienes según el Reglamento General de Protección de Datos de la UE (RGPD). Responsable del tratamiento: Qapilo.",
    sections: [
      {
        heading: "Datos que recopilamos",
        body: "Datos de la cuenta (nombre, correo y una contraseña cifrada de forma segura), tu progreso de aprendizaje (XP, rachas, niveles, insignias, lecciones completadas, favoritos), tus mensajes con el Tutor IA, tu preferencia de idioma y —si te suscribes— tu ID y estado de suscripción de PayPal. Nunca vemos ni almacenamos los datos de tu tarjeta.",
      },
      {
        heading: "Por qué los usamos (base jurídica)",
        body: "Tratamos tus datos para ofrecer la app y tu cuenta (ejecución de un contrato), recordar tu progreso y preferencias, y operar el Tutor IA y las suscripciones. Las funciones opcionales se basan en tu consentimiento, que puedes retirar en cualquier momento.",
      },
      {
        heading: "Servicios de terceros",
        body: "Para operar la app compartimos los datos mínimos necesarios con: Emergent (nuestro proveedor de alojamiento/infraestructura, que también reenvía los mensajes del Tutor de IA al modelo Claude de Anthropic, envía correos transaccionales en nuestro nombre y gestiona parte del proceso de inicio de sesión con Google), PayPal (procesamiento de pagos), Finnhub (datos de mercado en vivo), Anthropic (respuestas del Tutor de IA), Tavily (noticias, solo si está activado) y Google (solo si eliges iniciar sesión con Google). Cada uno procesa los datos según su propia política de privacidad y, cuando sea necesario, un acuerdo de procesamiento de datos.",
      },
      {
        heading: "Conservación de datos",
        body: "Conservamos tus datos mientras exista tu cuenta. Cuando eliminas tu cuenta, tu perfil y tu historial de chat se eliminan de forma permanente de nuestros sistemas.",
      },
      {
        heading: "Tus derechos (RGPD)",
        body: "Tienes derecho a acceder, corregir, exportar y eliminar tus datos, a oponerte o limitar el tratamiento y a retirar el consentimiento. Puedes exportar tus datos y eliminar tu cuenta en cualquier momento desde Perfil. También puedes presentar una reclamación ante tu autoridad de protección de datos.",
      },
      {
        heading: "Seguridad de los datos",
        body: "Las contraseñas se cifran, los datos se transmiten por conexiones cifradas y el acceso está restringido. Ningún método de transmisión es 100 % seguro, pero tomamos medidas razonables para proteger tu información.",
      },
      {
        heading: "Menores",
        body: "Qapilo no está dirigido a menores de 16 años. No recopilamos datos de menores a sabiendas. Si crees que un menor nos ha facilitado datos, contáctanos y los eliminaremos.",
      },
      {
        heading: "Cambios y contacto",
        body: `Podemos actualizar esta política e indicaremos la fecha arriba. Para cualquier solicitud de privacidad, contáctanos en ${CONTACT}.`,
      },
    ],
  },
};

export function getPrivacy(lang: Lang): Policy {
  return PRIVACY[lang] || PRIVACY.en;
}
