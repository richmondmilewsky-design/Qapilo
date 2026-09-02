import type { Lang } from "@/src/i18n/translations";

type Section = { heading: string; body: string };
type Doc = { title: string; intro: string; sections: Section[] };
export type DocType = "terms" | "ai" | "market" | "correct";

const CONTACT = "privacy@qapilo.de";

const DOCS: Record<DocType, Record<Lang, Doc>> = {
  terms: {
    en: {
      title: "Terms of Service",
      intro: "By using Qapilo you agree to these terms.",
      sections: [
        { heading: "Use of the App", body: "Qapilo provides gamified, educational content about investing. You agree to use it lawfully and not to misuse, copy, or disrupt the service." },
        { heading: "Accounts", body: "You are responsible for your account and for keeping your login secure. You must provide accurate information and be at least 16 years old." },
        { heading: "Subscriptions", body: "Qapilo Pro is an auto-renewing subscription offered after a free trial. You can cancel at any time; billing is handled by PayPal under its own terms." },
        { heading: "No Financial Advice", body: "All content is educational only and never a recommendation to buy, sell, or hold any security. See our Financial Disclaimer." },
        { heading: "Availability & Changes", body: "We may update, suspend, or discontinue features at any time. We may revise these terms and will indicate changes in the app." },
        { heading: "Contact", body: `Questions about these terms: ${CONTACT}.` },
      ],
    },
    de: {
      title: "Nutzungsbedingungen",
      intro: "Durch die Nutzung von Qapilo stimmst du diesen Bedingungen zu.",
      sections: [
        { heading: "Nutzung der App", body: "Qapilo bietet spielerische, edukative Inhalte über das Investieren. Du verpflichtest dich zur rechtmäßigen Nutzung und dazu, den Dienst nicht zu missbrauchen, zu kopieren oder zu stören." },
        { heading: "Konten", body: "Du bist für dein Konto und die Sicherheit deiner Anmeldedaten verantwortlich. Du musst korrekte Angaben machen und mindestens 16 Jahre alt sein." },
        { heading: "Abonnements", body: "Qapilo Pro ist ein automatisch verlängerndes Abo nach einer kostenlosen Testphase. Du kannst jederzeit kündigen; die Abrechnung erfolgt über PayPal zu dessen Bedingungen." },
        { heading: "Keine Finanzberatung", body: "Alle Inhalte dienen nur der Bildung und sind nie eine Empfehlung zum Kauf, Verkauf oder Halten von Wertpapieren. Siehe unseren Haftungsausschluss." },
        { heading: "Verfügbarkeit & Änderungen", body: "Wir können Funktionen jederzeit aktualisieren, aussetzen oder einstellen. Wir können diese Bedingungen ändern und weisen in der App darauf hin." },
        { heading: "Kontakt", body: `Fragen zu diesen Bedingungen: ${CONTACT}.` },
      ],
    },
    es: {
      title: "Términos del Servicio",
      intro: "Al usar Qapilo aceptas estos términos.",
      sections: [
        { heading: "Uso de la app", body: "Qapilo ofrece contenido educativo y gamificado sobre inversión. Aceptas usarlo de forma lícita y no hacer un mal uso, copiar ni interrumpir el servicio." },
        { heading: "Cuentas", body: "Eres responsable de tu cuenta y de mantener segura tu sesión. Debes proporcionar información veraz y tener al menos 16 años." },
        { heading: "Suscripciones", body: "Qapilo Pro es una suscripción de renovación automática ofrecida tras una prueba gratuita. Puedes cancelar cuando quieras; el cobro lo gestiona PayPal según sus condiciones." },
        { heading: "Sin asesoramiento financiero", body: "Todo el contenido es solo educativo y nunca una recomendación de comprar, vender o mantener valores. Consulta nuestro Aviso Financiero." },
        { heading: "Disponibilidad y cambios", body: "Podemos actualizar, suspender o retirar funciones en cualquier momento. Podemos modificar estos términos e indicaremos los cambios en la app." },
        { heading: "Contacto", body: `Consultas sobre estos términos: ${CONTACT}.` },
      ],
    },
  },
  ai: {
    en: {
      title: "AI Transparency",
      intro: "How the Qapilo AI Tutor works and handles your data.",
      sections: [
        { heading: "What Powers It", body: "The AI Tutor is powered by Anthropic's Claude language model. It generates responses to help you learn investing concepts." },
        { heading: "What Is Sent", body: "When you send a message, its text (and recent conversation context) is transmitted to the AI provider to generate a reply. Avoid sharing sensitive personal information in chat." },
        { heading: "Live Data", body: "For questions about current prices, the Tutor may include live quotes from our market-data provider. It never invents figures it wasn't given." },
        { heading: "Limits & Accuracy", body: "AI can make mistakes and may be incomplete or outdated. Responses are educational only and are not financial advice." },
        { heading: "Sources & Methodology", body: "Qapilo's educational content (lessons, quizzes, and Educational AI Tutor responses) is based on generally accepted, publicly available financial and economic knowledge — including fundamentals of money, investing, stock markets, valuation ratios, financial statements, diversification, and behavioral finance. Content reflects definitions and concepts commonly used in standard financial education resources, rather than any single proprietary source. Responses from the Educational AI Tutor are generated by an AI language model based on its general training knowledge. The tutor does not have access to live market data, current news, or real-time prices; any companies mentioned serve only as neutral, illustrative examples. Specific figures, historical data, or ratios should always be independently verified — for example through official company filings, regulatory bodies, or established financial media — before making any decision. Qapilo does not replace individual financial, investment, or tax advice." },
        { heading: "Your Control", body: "You can clear your entire AI chat history at any time from Settings, and deleting your account removes it permanently." },
      ],
    },
    de: {
      title: "KI-Transparenz",
      intro: "Wie der Qapilo KI-Tutor funktioniert und mit deinen Daten umgeht.",
      sections: [
        { heading: "Was ihn antreibt", body: "Der KI-Tutor wird vom Sprachmodell Claude von Anthropic betrieben. Er erzeugt Antworten, die dir helfen, Anlagekonzepte zu lernen." },
        { heading: "Was gesendet wird", body: "Wenn du eine Nachricht sendest, wird ihr Text (und der jüngste Gesprächskontext) an den KI-Anbieter übertragen, um eine Antwort zu erzeugen. Teile keine sensiblen persönlichen Daten im Chat." },
        { heading: "Live-Daten", body: "Bei Fragen zu aktuellen Kursen kann der Tutor Live-Kurse unseres Marktdatenanbieters einbeziehen. Er erfindet nie Zahlen, die ihm nicht vorliegen." },
        { heading: "Grenzen & Genauigkeit", body: "KI kann Fehler machen und unvollständig oder veraltet sein. Antworten dienen nur der Bildung und sind keine Finanzberatung." },
        { heading: "Quellen & Methodik", body: "Die Bildungsinhalte von Qapilo (Lektionen, Quizfragen und Antworten des Educational AI Tutors) basieren auf allgemein anerkanntem, öffentlich zugänglichem Finanz- und Wirtschaftswissen – etwa Grundlagen zu Geld, Investieren, Aktienmärkten, Bewertungskennzahlen, Bilanzierung, Diversifikation und Verhaltensökonomie. Die Inhalte orientieren sich an gängigen, in Fachliteratur und öffentlichen Bildungsangeboten üblichen Definitionen und Konzepten, nicht an einer einzelnen, proprietären Quelle. Antworten des Educational AI Tutors werden von einem KI-Sprachmodell auf Basis seines allgemeinen Trainingswissens erzeugt. Der Tutor hat keinen Zugriff auf Live-Marktdaten, aktuelle Nachrichten oder Echtzeit-Kurse; genannte Unternehmen dienen ausschließlich als neutrale, illustrative Bildungsbeispiele. Konkrete Zahlen, historische Daten oder Kennzahlen sollten vor einer eigenen Entscheidung stets selbst überprüft werden, z. B. über offizielle Unternehmensberichte, Aufsichtsbehörden (z. B. BaFin) oder anerkannte Finanzmedien. Qapilo ersetzt keine individuelle Finanz-, Anlage- oder Steuerberatung." },
        { heading: "Deine Kontrolle", body: "Du kannst deinen gesamten KI-Chatverlauf jederzeit in den Einstellungen löschen; beim Löschen deines Kontos wird er dauerhaft entfernt." },
      ],
    },
    es: {
      title: "Transparencia de IA",
      intro: "Cómo funciona el Tutor IA de Qapilo y cómo trata tus datos.",
      sections: [
        { heading: "Qué lo impulsa", body: "El Tutor IA funciona con el modelo de lenguaje Claude de Anthropic. Genera respuestas para ayudarte a aprender conceptos de inversión." },
        { heading: "Qué se envía", body: "Cuando envías un mensaje, su texto (y el contexto reciente de la conversación) se transmite al proveedor de IA para generar una respuesta. Evita compartir datos personales sensibles en el chat." },
        { heading: "Datos en vivo", body: "Para preguntas sobre precios actuales, el Tutor puede incluir cotizaciones en vivo de nuestro proveedor de datos de mercado. Nunca inventa cifras que no se le hayan dado." },
        { heading: "Límites y precisión", body: "La IA puede equivocarse y estar incompleta o desactualizada. Las respuestas son solo educativas y no son asesoramiento financiero." },
        { heading: "Fuentes y metodología", body: "El contenido educativo de Qapilo (lecciones, cuestionarios y respuestas del Tutor Educativo con IA) se basa en conocimientos financieros y económicos generalmente aceptados y disponibles públicamente, incluyendo conceptos básicos sobre el dinero, la inversión, los mercados bursátiles, los ratios de valoración, los estados financieros, la diversificación y las finanzas conductuales. El contenido refleja definiciones y conceptos habituales en materiales de educación financiera estándar, no una única fuente propietaria. Las respuestas del Tutor Educativo con IA son generadas por un modelo de lenguaje de IA a partir de su conocimiento general de entrenamiento. El tutor no tiene acceso a datos de mercado en tiempo real, noticias actuales ni cotizaciones en vivo; las empresas mencionadas sirven únicamente como ejemplos educativos neutrales. Las cifras concretas, datos históricos o ratios deben verificarse siempre de forma independiente antes de tomar cualquier decisión. Qapilo no sustituye el asesoramiento financiero, de inversión o fiscal individual." },
        { heading: "Tu control", body: "Puedes borrar todo tu historial de chat con la IA en cualquier momento desde Ajustes; al eliminar tu cuenta se borra de forma permanente." },
      ],
    },
  },
  market: {
    en: {
      title: "Market Data Sources",
      intro: "Where Qapilo's stock information comes from.",
      sections: [
        { heading: "Live Quotes", body: "Real-time stock prices are provided by Finnhub. Prices are cached briefly and may be delayed or differ slightly from your broker." },
        { heading: "Price Charts", body: "Historical price charts shown in the app are illustrative and simulated for education; they are not exact historical trading data." },
        { heading: "Company Logos", body: "Company logos are loaded from a third-party logo service based on the company's domain." },
        { heading: "Not for Trading", body: "All market data is for educational use only and must not be relied upon for real trading or investment decisions." },
      ],
    },
    de: {
      title: "Marktdatenquellen",
      intro: "Woher die Aktieninformationen von Qapilo stammen.",
      sections: [
        { heading: "Live-Kurse", body: "Echtzeit-Aktienkurse werden von Finnhub bereitgestellt. Kurse werden kurz zwischengespeichert und können verzögert sein oder leicht von deinem Broker abweichen." },
        { heading: "Kurscharts", body: "Die in der App gezeigten historischen Kurscharts sind illustrativ und zu Bildungszwecken simuliert; sie sind keine exakten historischen Handelsdaten." },
        { heading: "Firmenlogos", body: "Firmenlogos werden von einem Drittanbieter anhand der Domain des Unternehmens geladen." },
        { heading: "Nicht zum Handeln", body: "Alle Marktdaten dienen nur der Bildung und dürfen nicht für echte Handels- oder Anlageentscheidungen herangezogen werden." },
      ],
    },
    es: {
      title: "Fuentes de datos de mercado",
      intro: "De dónde proviene la información bursátil de Qapilo.",
      sections: [
        { heading: "Cotizaciones en vivo", body: "Los precios en tiempo real los proporciona Finnhub. Los precios se almacenan en caché brevemente y pueden estar retrasados o diferir ligeramente de tu bróker." },
        { heading: "Gráficos de precios", body: "Los gráficos históricos que se muestran en la app son ilustrativos y simulados con fines educativos; no son datos exactos de negociación histórica." },
        { heading: "Logotipos de empresas", body: "Los logotipos se cargan desde un servicio de terceros según el dominio de la empresa." },
        { heading: "No para operar", body: "Todos los datos de mercado son solo educativos y no deben usarse para operar ni tomar decisiones de inversión reales." },
      ],
    },
  },
  correct: {
    en: {
      title: "Correct My Data",
      intro: "Under GDPR you can correct inaccurate personal data.",
      sections: [
        { heading: "Edit Your Name", body: "You can update your display name below. It is saved immediately to your account." },
        { heading: "Other Corrections", body: `To correct your email or any other data, contact us at ${CONTACT} and we will update it promptly.` },
      ],
    },
    de: {
      title: "Meine Daten korrigieren",
      intro: "Nach der DSGVO kannst du unrichtige personenbezogene Daten korrigieren.",
      sections: [
        { heading: "Namen bearbeiten", body: "Du kannst deinen Anzeigenamen unten aktualisieren. Er wird sofort in deinem Konto gespeichert." },
        { heading: "Weitere Korrekturen", body: `Um deine E-Mail oder andere Daten zu korrigieren, kontaktiere uns unter ${CONTACT}; wir aktualisieren sie umgehend.` },
      ],
    },
    es: {
      title: "Corregir mis datos",
      intro: "Según el RGPD puedes corregir datos personales inexactos.",
      sections: [
        { heading: "Editar tu nombre", body: "Puedes actualizar tu nombre visible abajo. Se guarda de inmediato en tu cuenta." },
        { heading: "Otras correcciones", body: `Para corregir tu correo u otros datos, contáctanos en ${CONTACT} y lo actualizaremos rápidamente.` },
      ],
    },
  },
};

export function getDoc(type: DocType, lang: Lang): Doc {
  return DOCS[type][lang] || DOCS[type].en;
}
