import type { Lang } from "@/src/i18n/translations";

type Section = { heading: string; body: string };
type Disclaimer = { intro: string; sections: Section[] };

const DISCLAIMER: Record<Lang, Disclaimer> = {
  en: {
    intro: "Please read this disclaimer carefully before using Qapilo.",
    sections: [
      {
        heading: "Educational Purposes Only",
        body: "This app is provided solely for educational and informational purposes. The content, examples, explanations, stock data, charts, and other materials available in this app are intended to help users learn the basics of investing, stocks, and personal finance.",
      },
      {
        heading: "Not Financial Advice",
        body: "I am not a licensed financial advisor, investment advisor, broker, accountant, or financial professional. I do not hold any financial certifications, and nothing in this app should be considered financial, investment, legal, or tax advice.",
      },
      {
        heading: "No Investment Recommendations",
        body: "Any stocks, ETFs, or other financial assets shown in this app are used only as educational examples to demonstrate financial concepts. Their appearance in the app does not constitute a recommendation, endorsement, or suggestion to buy, sell, or hold any investment.",
      },
      {
        heading: "Invest at Your Own Risk",
        body: "All investments involve risk, including the possible loss of your entire investment. Past performance does not guarantee future results. Before making any investment decisions, you should conduct your own research and consider consulting a qualified financial advisor.",
      },
      {
        heading: "Accuracy of Information",
        body: "While every effort is made to provide accurate and up-to-date information, I cannot guarantee that all information, including live market data, is complete, accurate, or current. I am not responsible for any errors, omissions, delays, or losses resulting from the use of this app.",
      },
      {
        heading: "Acceptance of This Disclaimer",
        body: "By using this app, you acknowledge that you understand and accept this disclaimer. You agree that you are solely responsible for your own financial decisions and that the developer of this app is not liable for any financial losses or damages arising from the use of the app or the information it contains.",
      },
    ],
  },
  de: {
    intro: "Bitte lies diesen Haftungsausschluss sorgfältig, bevor du Qapilo nutzt.",
    sections: [
      {
        heading: "Nur zu Bildungszwecken",
        body: "Diese App dient ausschließlich zu Bildungs- und Informationszwecken. Die Inhalte, Beispiele, Erklärungen, Aktiendaten, Charts und sonstigen Materialien in dieser App sollen den Nutzern helfen, die Grundlagen des Investierens, von Aktien und persönlichen Finanzen zu erlernen.",
      },
      {
        heading: "Keine Finanzberatung",
        body: "Ich bin kein zugelassener Finanzberater, Anlageberater, Broker, Buchhalter oder Finanzfachmann. Ich besitze keine finanziellen Zertifizierungen, und nichts in dieser App ist als Finanz-, Anlage-, Rechts- oder Steuerberatung zu verstehen.",
      },
      {
        heading: "Keine Anlageempfehlungen",
        body: "Alle in dieser App gezeigten Aktien, ETFs oder anderen Finanzwerte dienen ausschließlich als Bildungsbeispiele zur Veranschaulichung von Finanzkonzepten. Ihr Erscheinen in der App stellt keine Empfehlung, Befürwortung oder Aufforderung dar, eine Anlage zu kaufen, zu verkaufen oder zu halten.",
      },
      {
        heading: "Investieren auf eigenes Risiko",
        body: "Jede Anlage ist mit Risiken verbunden, einschließlich des möglichen Verlusts des gesamten investierten Kapitals. Die Wertentwicklung in der Vergangenheit ist keine Garantie für zukünftige Ergebnisse. Bevor du Anlageentscheidungen triffst, solltest du eigene Recherchen anstellen und einen qualifizierten Finanzberater hinzuziehen.",
      },
      {
        heading: "Richtigkeit der Informationen",
        body: "Obwohl ich mich um genaue und aktuelle Informationen bemühe, kann ich nicht garantieren, dass alle Informationen, einschließlich Live-Marktdaten, vollständig, korrekt oder aktuell sind. Ich hafte nicht für Fehler, Auslassungen, Verzögerungen oder Verluste, die aus der Nutzung dieser App entstehen.",
      },
      {
        heading: "Annahme dieses Haftungsausschlusses",
        body: "Durch die Nutzung dieser App bestätigst du, dass du diesen Haftungsausschluss verstehst und akzeptierst. Du erklärst dich damit einverstanden, dass du allein für deine finanziellen Entscheidungen verantwortlich bist und dass der Entwickler dieser App nicht für finanzielle Verluste oder Schäden haftet, die aus der Nutzung der App oder der darin enthaltenen Informationen entstehen.",
      },
    ],
  },
  es: {
    intro: "Lee este aviso legal con atención antes de usar Qapilo.",
    sections: [
      {
        heading: "Solo con fines educativos",
        body: "Esta app se ofrece únicamente con fines educativos e informativos. El contenido, los ejemplos, las explicaciones, los datos de acciones, los gráficos y demás materiales disponibles en esta app están destinados a ayudar a los usuarios a aprender los conceptos básicos de la inversión, las acciones y las finanzas personales.",
      },
      {
        heading: "No es asesoramiento financiero",
        body: "No soy asesor financiero, asesor de inversiones, corredor, contable ni profesional financiero con licencia. No poseo ninguna certificación financiera, y nada en esta app debe considerarse asesoramiento financiero, de inversión, legal o fiscal.",
      },
      {
        heading: "Sin recomendaciones de inversión",
        body: "Cualquier acción, ETF u otro activo financiero mostrado en esta app se usa solo como ejemplo educativo para ilustrar conceptos financieros. Su aparición en la app no constituye una recomendación, respaldo ni sugerencia de comprar, vender o mantener ninguna inversión.",
      },
      {
        heading: "Invierte bajo tu propia responsabilidad",
        body: "Toda inversión implica riesgos, incluida la posible pérdida de la totalidad de tu inversión. El rendimiento pasado no garantiza resultados futuros. Antes de tomar cualquier decisión de inversión, debes investigar por tu cuenta y considerar consultar a un asesor financiero cualificado.",
      },
      {
        heading: "Exactitud de la información",
        body: "Aunque se hace todo lo posible por ofrecer información precisa y actualizada, no puedo garantizar que toda la información, incluidos los datos de mercado en vivo, sea completa, exacta o actual. No me hago responsable de errores, omisiones, retrasos o pérdidas derivados del uso de esta app.",
      },
      {
        heading: "Aceptación de este aviso legal",
        body: "Al usar esta app, reconoces que entiendes y aceptas este aviso legal. Aceptas que eres el único responsable de tus decisiones financieras y que el desarrollador de esta app no es responsable de pérdidas o daños financieros derivados del uso de la app o de la información que contiene.",
      },
    ],
  },
};

export function getDisclaimer(lang: Lang): Disclaimer {
  return DISCLAIMER[lang] || DISCLAIMER.en;
}
