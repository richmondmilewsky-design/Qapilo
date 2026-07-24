# German (de) and Spanish (es) translations for curriculum + stock explanations.
# English is the source (content.py) and the fallback. Quiz answer INDICES are
# unchanged — only the visible text is translated, so option order must match content.py.

UNIT_T = {
    "de": {
        "u1": {"title": "Börsen-Grundlagen", "subtitle": "Was Aktien sind und warum es sie gibt"},
        "u2": {"title": "Wie Aktien funktionieren", "subtitle": "Kurse, Dividenden und Renditen"},
        "u3": {"title": "Den Markt lesen", "subtitle": "Indizes, Orders und Charts"},
        "u4": {"title": "Fundamentalanalyse", "subtitle": "Den Wert eines Unternehmens beurteilen"},
        "u5": {"title": "Klug investieren", "subtitle": "Strategien, die sich bewährt haben"},
    },
    "es": {
        "u1": {"title": "Fundamentos de la bolsa", "subtitle": "Qué son las acciones y por qué existen"},
        "u2": {"title": "Cómo funcionan las acciones", "subtitle": "Precios, dividendos y rentabilidad"},
        "u3": {"title": "Leer el mercado", "subtitle": "Índices, órdenes y gráficos"},
        "u4": {"title": "Análisis fundamental", "subtitle": "Cómo juzgar el valor de una empresa"},
        "u5": {"title": "Invertir con cabeza", "subtitle": "Estrategias que resisten el paso del tiempo"},
    },
}

LESSON_T = {
    "de": {
        "l1": {"title": "Was ist eine Aktie?",
            "cards": [
                {"heading": "Ein Anteil am Eigentum", "body": "Eine Aktie ist ein winziger Eigentumsanteil an einem Unternehmen. Kaufst du eine Aktie, besitzt du buchstäblich ein Stück dieses Unternehmens."},
                {"heading": "Warum Unternehmen Aktien verkaufen", "body": "Unternehmen verkaufen Aktien, um Geld für Wachstum zu beschaffen – Fabriken bauen, Leute einstellen oder Produkte einführen – ohne Schulden aufzunehmen."},
                {"heading": "Du bist Aktionär", "body": "Als Aktionär kannst du profitieren, wenn das Unternehmen an Wert gewinnt, und manchmal einen Gewinnanteil erhalten, die sogenannte Dividende."}],
            "questions": [
                {"q": "Was bedeutet der Besitz einer Aktie?", "options": ["Ein Kredit an das Unternehmen", "Ein Eigentumsanteil am Unternehmen", "Ein garantiertes Monatsgehalt", "Eine Staatsanleihe"], "explain": "Eine Aktie ist Teileigentum an einem Unternehmen."},
                {"q": "Warum geben Unternehmen Aktien aus?", "options": ["Um Geld für Wachstum zu beschaffen", "Um Steuern zu zahlen", "Um keine Produkte herzustellen", "Um ihren Wert zu senken"], "explain": "Die Ausgabe von Aktien beschafft Kapital ohne Kreditaufnahme."},
                {"q": "Wer Aktien besitzt, heißt…", "options": ["Kreditgeber", "Aktionär", "Kunde", "Prüfer"], "explain": "Besitzer von Aktien sind Aktionäre."}]},
        "l2": {"title": "Börsen",
            "cards": [
                {"heading": "Der Marktplatz", "body": "Eine Börse ist ein Marktplatz, an dem Käufer und Verkäufer Aktien handeln. Die NYSE und die Nasdaq gehören zu den größten."},
                {"heading": "Orders zusammenführen", "body": "Börsen führen Kauf- und Verkaufsaufträge zusammen und veröffentlichen den aktuellen Kurs, den alle sehen können – das hält den Handel fair und transparent."},
                {"heading": "Tickersymbole", "body": "Jedes Unternehmen erhält ein kurzes Tickersymbol – AAPL für Apple, TSLA für Tesla – um die Aktie schnell zu finden und zu handeln."}],
            "questions": [
                {"q": "Was ist eine Börse?", "options": ["Ein Banktresor", "Ein Marktplatz zum Handel mit Aktien", "Eine Art Steuer", "Das Lager eines Unternehmens"], "explain": "Börsen sind Marktplätze, die Käufer und Verkäufer zusammenbringen."},
                {"q": "AAPL ist das Tickersymbol für…", "options": ["Amazon", "Apple", "Alphabet", "AMD"], "explain": "AAPL steht für Apple Inc."},
                {"q": "Welche ist eine große US-Börse?", "options": ["Nasdaq", "FIFA", "NASA", "IKEA"], "explain": "Die Nasdaq ist eine große Börse, ebenso die NYSE."}]},
        "l3": {"title": "Bullen vs. Bären",
            "cards": [
                {"heading": "Bullenmarkt", "body": "Ein Bullenmarkt herrscht, wenn die Kurse steigen und der Optimismus hoch ist. Stell dir einen Bullen vor, der seine Hörner nach oben stößt."},
                {"heading": "Bärenmarkt", "body": "Ein Bärenmarkt ist ein anhaltender Rückgang von 20 % oder mehr, mit Pessimismus. Stell dir einen Bären vor, der seine Pranke nach unten schlägt."},
                {"heading": "Stimmung bewegt Märkte", "body": "Kurse spiegeln wider, wie hoffnungsvoll oder ängstlich Anleger in die Zukunft blicken – nicht nur die heutigen Fakten."}],
            "questions": [
                {"q": "Ein steigender, optimistischer Markt heißt…", "options": ["Bärenmarkt", "Bullenmarkt", "Flacher Markt", "Toter Markt"], "explain": "Bullen stürmen nach oben – steigende Kurse."},
                {"q": "Ein Bärenmarkt bedeutet meist, dass die Kurse…", "options": ["stark steigen", "exakt gleich bleiben", "deutlich fallen", "gelöscht werden"], "explain": "Bärenmärkte sind längere Rückgänge von 20 %+."},
                {"q": "Marktstimmung bezeichnet…", "options": ["die Stimmung und Erwartung der Anleger", "die Gebäudetemperatur", "die Unternehmenslöhne", "die Steuersätze"], "explain": "Stimmung ist die kollektive Laune der Anleger."}]},
        "l4": {"title": "Was Kurse bewegt",
            "cards": [
                {"heading": "Angebot und Nachfrage", "body": "Wollen mehr Menschen eine Aktie kaufen als verkaufen, steigt der Kurs. Wollen mehr verkaufen, fällt er."},
                {"heading": "Nachrichten und Gewinne", "body": "Starke Gewinne, neue Produkte oder gute Nachrichten locken Käufer an. Schlechte Nachrichten oder schwache Gewinne drücken die Kurse."},
                {"heading": "Der gesamte Markt", "body": "Zinsen, die Wirtschaft und globale Ereignisse können nahezu alle Aktien gleichzeitig bewegen."}],
            "questions": [
                {"q": "Übersteigt die Nachfrage nach einer Aktie das Angebot, tendiert der Kurs dazu, zu…", "options": ["fallen", "steigen", "einzufrieren", "verschwinden"], "explain": "Mehr Käufer als Verkäufer treiben die Kurse nach oben."},
                {"q": "Was steigert oft einen Aktienkurs?", "options": ["Ein starker Gewinnbericht", "Ein Produktrückruf", "Ein verlorener Prozess", "Sinkende Umsätze"], "explain": "Gute Gewinne locken Käufer an."},
                {"q": "Was kann fast alle Aktien gleichzeitig bewegen?", "options": ["Die Meinung eines einzelnen Kunden", "Zinsänderungen", "Ein einzelner Tweet ohne Reichweite", "Das Firmenlogo"], "explain": "Makrofaktoren wie Zinsen betreffen den ganzen Markt."}]},
        "l5": {"title": "Dividenden",
            "cards": [
                {"heading": "Den Gewinn teilen", "body": "Eine Dividende ist eine Barzahlung, die manche Unternehmen aus ihren Gewinnen an Aktionäre schicken, oft vierteljährlich."},
                {"heading": "Dividendenrendite", "body": "Rendite = jährliche Dividende ÷ Aktienkurs. Eine Dividende von 2 $ bei einer 100-$-Aktie ergibt 2 % Rendite."},
                {"heading": "Nicht alle zahlen", "body": "Schnell wachsende Unternehmen reinvestieren Gewinne oft, statt Dividenden zu zahlen, um größeres künftiges Wachstum zu erzielen."}],
            "questions": [
                {"q": "Eine Dividende ist…", "options": ["eine Strafgebühr", "ein Gewinnanteil, der an Eigentümer gezahlt wird", "eine Art Kredit", "eine Handelssteuer"], "explain": "Dividenden verteilen Gewinne an Aktionäre."},
                {"q": "Eine jährliche Dividende von 4 $ bei einer 100-$-Aktie ergibt eine Rendite von…", "options": ["0,4 %", "4 %", "40 %", "14 %"], "explain": "4 ÷ 100 = 4 %."},
                {"q": "Wachstumsunternehmen…", "options": ["reinvestieren Gewinne, statt Dividenden zu zahlen", "zahlen immer riesige Dividenden", "machen nie Gewinn", "zahlen täglich Dividenden"], "explain": "Sie reinvestieren, um Wachstum anzutreiben."}]},
        "l6": {"title": "Risiko & Rendite",
            "cards": [
                {"heading": "Der Kompromiss", "body": "Höhere mögliche Renditen gehen meist mit höherem Risiko einher. Sicherere Anlagen wachsen tendenziell langsamer."},
                {"heading": "Volatilität", "body": "Volatilität ist, wie stark ein Kurs auf- und abschwankt. Hohe Volatilität bedeutet größere, schnellere Bewegungen."},
                {"heading": "Anlagehorizont", "body": "Je länger du investiert bleiben kannst, desto mehr glätten sich kurzfristige Schwankungen."}],
            "questions": [
                {"q": "Höhere mögliche Rendite bedeutet meist…", "options": ["geringeres Risiko", "höheres Risiko", "kein Risiko", "garantierten Gewinn"], "explain": "Risiko und Ertrag bewegen sich zusammen."},
                {"q": "Volatilität misst…", "options": ["das Alter des Unternehmens", "die Größe der Kursschwankungen", "die Zahl der Mitarbeiter", "die Dividendentermine"], "explain": "Volatilität ist die Größe der Kursschwankungen."},
                {"q": "Ein längerer Anlagehorizont neigt dazu…", "options": ["tägliche Schwankungen ewig zu verstärken", "kurzfristige Schwankungen zu glätten", "Verluste zu garantieren", "jedes Risiko zu beseitigen"], "explain": "Zeit hilft, Volatilität zu glätten."}]},
        "l7": {"title": "Marktindizes",
            "cards": [
                {"heading": "Eine Anzeigetafel des Marktes", "body": "Ein Index verfolgt eine Gruppe von Aktien, um zu zeigen, wie sich ein Markt insgesamt entwickelt – wie eine Anzeigetafel."},
                {"heading": "Bekannte Indizes", "body": "Der S&P 500 verfolgt 500 große US-Unternehmen. Der Nasdaq-100 ist techlastig. Der Dow verfolgt 30 große Namen."},
                {"heading": "Warum sie wichtig sind", "body": "Indizes sind Vergleichsmaßstäbe. Anleger vergleichen ihre Renditen damit, um zu sehen, ob sie den Markt schlagen."}],
            "questions": [
                {"q": "Ein Aktienindex lässt sich am besten beschreiben als…", "options": ["ein einzelnes Unternehmen", "eine Anzeigetafel für eine Gruppe von Aktien", "ein Bankkonto", "ein Steuerformular"], "explain": "Indizes fassen eine Gruppe von Aktien zusammen."},
                {"q": "Der S&P 500 verfolgt etwa…", "options": ["5 Unternehmen", "50 Unternehmen", "500 große US-Unternehmen", "5000 Unternehmen"], "explain": "Er verfolgt 500 große US-Firmen."},
                {"q": "Anleger nutzen Indizes als…", "options": ["Vergleichsmaßstab für Renditen", "Kochrezepte", "Rechtsverträge", "Passwörter"], "explain": "Indizes sind Leistungsmaßstäbe."}]},
        "l8": {"title": "Orderarten",
            "cards": [
                {"heading": "Market-Order", "body": "Eine Market-Order kauft oder verkauft sofort zum besten verfügbaren Kurs. Schnell, aber der genaue Kurs ist nicht garantiert."},
                {"heading": "Limit-Order", "body": "Eine Limit-Order wird nur zu deinem gewählten Kurs oder besser ausgeführt. Du steuerst den Kurs, aber sie wird evtl. nicht ausgeführt."},
                {"heading": "Stop-Order", "body": "Eine Stop-Order löst einen Handel aus, sobald ein Kursniveau erreicht ist – oft genutzt, um Verluste zu begrenzen."}],
            "questions": [
                {"q": "Eine Market-Order priorisiert…", "options": ["den genauen Kurs", "die Ausführungsgeschwindigkeit", "das Vermeiden von Trades", "Dividenden"], "explain": "Market-Orders werden schnell zum besten verfügbaren Kurs ausgeführt."},
                {"q": "Mit einer Limit-Order kannst du…", "options": ["den Kurs festlegen, den du akzeptierst", "die Börse umgehen", "eine Ausführung garantieren", "alle Gebühren vermeiden"], "explain": "Limit-Orders steuern den Ausführungskurs."},
                {"q": "Eine Stop-Order wird oft genutzt, um…", "options": ["mögliche Verluste zu begrenzen", "Dividenden zu zahlen", "ein Unternehmen zu gründen", "die Volatilität zu erhöhen"], "explain": "Stops helfen, Verluste zu deckeln."}]},
        "l9": {"title": "Einen Chart lesen",
            "cards": [
                {"heading": "Kurs über Zeit", "body": "Ein Chart trägt den Kurs auf der senkrechten Achse und die Zeit unten ab und zeigt die Geschichte der Kursbewegungen einer Aktie."},
                {"heading": "Trends", "body": "Ein Aufwärtstrend bildet höhere Hochs und höhere Tiefs. Ein Abwärtstrend bildet tiefere Hochs und tiefere Tiefs."},
                {"heading": "Volumen", "body": "Das Volumen zeigt, wie viele Aktien gehandelt wurden. Große Bewegungen bei hohem Volumen gelten als aussagekräftiger."}],
            "questions": [
                {"q": "Auf einem üblichen Chart wird die Zeit dargestellt auf der…", "options": ["senkrechten Achse", "waagerechten Achse", "dem Firmenlogo", "dem Ticker"], "explain": "Die Zeit verläuft entlang der waagerechten Achse."},
                {"q": "Ein Aufwärtstrend ist eine Folge von…", "options": ["tieferen Hochs und tieferen Tiefs", "höheren Hochs und höheren Tiefs", "nur flachen Linien", "zufälligen Punkten"], "explain": "Aufwärtstrends steigen mit höheren Hochs und Tiefs."},
                {"q": "Das Handelsvolumen misst…", "options": ["gehandelte Aktien", "das Alter des Unternehmens", "die Dividendenhöhe", "das Gehalt des CEO"], "explain": "Volumen ist die Zahl der gehandelten Aktien."}]},
        "l10": {"title": "Gewinn & Umsatz",
            "cards": [
                {"heading": "Umsatz vs. Gewinn", "body": "Umsatz ist das gesamte eingehende Geld. Gewinn ist das, was nach Abzug aller Kosten übrig bleibt."},
                {"heading": "Berichtssaison", "body": "Jedes Quartal berichten Unternehmen ihre Ergebnisse. Erwartungen zu übertreffen hebt oft die Aktie; sie zu verfehlen kann sie fallen lassen."},
                {"heading": "EPS", "body": "Der Gewinn je Aktie (EPS) ist der Gewinn geteilt durch die Zahl der Aktien – ein schneller Blick auf die Profitabilität je Aktie."}],
            "questions": [
                {"q": "Gewinn ist der Umsatz minus…", "options": ["nichts", "alle Kosten und Ausgaben", "nur Dividenden", "der Aktienkurs"], "explain": "Gewinn ist, was nach den Kosten übrig bleibt."},
                {"q": "EPS steht für…", "options": ["Extra Profit Summe", "Gewinn je Aktie (Earnings Per Share)", "Eigenkapital-Preis-Skala", "Exchange-Priority-System"], "explain": "EPS = Earnings Per Share (Gewinn je Aktie)."},
                {"q": "Gewinnerwartungen zu übertreffen…", "options": ["hebt oft die Aktie", "nimmt das Unternehmen von der Börse", "streicht Dividenden", "hat nie eine Wirkung"], "explain": "Übertreffen treibt die Kurse tendenziell nach oben."}]},
        "l11": {"title": "Das KGV",
            "cards": [
                {"heading": "Kurs-Gewinn-Verhältnis", "body": "Das KGV = Aktienkurs ÷ Gewinn je Aktie. Es zeigt, wie viel Anleger für 1 $ Gewinn zahlen."},
                {"heading": "Hoch vs. niedrig", "body": "Ein hohes KGV kann hohe Wachstumserwartungen bedeuten – oder eine überteuerte Aktie. Ein niedriges KGV kann Wert oder Probleme signalisieren."},
                {"heading": "Fair vergleichen", "body": "Das KGV ist am nützlichsten, wenn man ähnliche Unternehmen derselben Branche vergleicht."}],
            "questions": [
                {"q": "Das KGV vergleicht den Kurs mit…", "options": ["dem Umsatz", "dem Gewinn je Aktie", "den Dividenden", "dem Volumen"], "explain": "KGV = Kurs ÷ Gewinn je Aktie."},
                {"q": "Ein sehr hohes KGV spiegelt oft wider…", "options": ["hohe Wachstumserwartungen", "null Zinsen", "einen garantierten Crash", "nie Gewinne"], "explain": "Ein hohes KGV impliziert Wachstumserwartungen."},
                {"q": "Das KGV ist am aussagekräftigsten, wenn…", "options": ["man ähnliche Unternehmen vergleicht", "man eine Bank mit einer Bäckerei vergleicht", "man die Branche ignoriert", "man es auf Zufallszahlen anwendet"], "explain": "Vergleiche innerhalb derselben Branche."}]},
        "l12": {"title": "Marktkapitalisierung",
            "cards": [
                {"heading": "Unternehmensgröße", "body": "Marktkapitalisierung = Aktienkurs × Gesamtzahl der Aktien. Es ist das Preisschild des Marktes für das ganze Unternehmen."},
                {"heading": "Größenklassen", "body": "Large-Cap (riesig, stabil), Mid-Cap (wachsend) und Small-Cap (kleiner, riskanter, höheres Wachstumspotenzial)."},
                {"heading": "Kurs ≠ Größe", "body": "Eine 500-$-Aktie ist nicht automatisch größer als eine 10-$-Aktie – es kommt darauf an, wie viele Aktien existieren."}],
            "questions": [
                {"q": "Die Marktkapitalisierung ist der Aktienkurs mal…", "options": ["die gesamten ausstehenden Aktien", "das KGV", "der Umsatz", "die Dividendenrendite"], "explain": "Marktkap. = Kurs × Aktien."},
                {"q": "Large-Cap-Unternehmen sind im Allgemeinen…", "options": ["winzig und riskant", "riesig und stabiler", "immer unprofitabel", "nur privat"], "explain": "Large-Caps sind groß und relativ stabil."},
                {"q": "Ein höherer Aktienkurs allein bedeutet, dass das Unternehmen größer ist. Richtig oder falsch?", "options": ["Richtig", "Falsch"], "explain": "Die Größe hängt auch von den ausstehenden Aktien ab."}]},
        "l13": {"title": "Diversifikation",
            "cards": [
                {"heading": "Nicht alles auf eine Karte setzen", "body": "Geld auf viele Aktien und Branchen zu verteilen, verringert den Schaden, falls eine einzelne fällt."},
                {"heading": "Fonds machen es einfach", "body": "Indexfonds und ETFs bündeln Hunderte Aktien in einem Kauf – sofortige Diversifikation."},
                {"heading": "Weniger Risiko, ruhigere Fahrt", "body": "Diversifikation beseitigt nicht jedes Risiko, glättet aber Renditen und schützt vor Einzelkatastrophen."}],
            "questions": [
                {"q": "Diversifikation bedeutet…", "options": ["nur eine Aktie zu kaufen", "Anlagen auf viele zu verteilen", "den Markt täglich zu timen", "alle Aktien zu meiden"], "explain": "Verteile das Risiko auf viele Positionen."},
                {"q": "Eine einfache Art zu diversifizieren ist der Kauf von…", "options": ["einem Indexfonds oder ETF", "einer einzelnen Aktie", "nur der Aktie des Arbeitgebers", "Lottoscheinen"], "explain": "ETFs bündeln viele Aktien auf einmal."},
                {"q": "Diversifikation reduziert vor allem…", "options": ["das Risiko einzelner Unternehmen", "dein Alter", "die Handelszeiten", "die Tickerlänge"], "explain": "Sie dämpft Einbrüche einzelner Unternehmen."}]},
        "l14": {"title": "Cost-Average-Effekt",
            "cards": [
                {"heading": "Nach Plan investieren", "body": "Der Cost-Average-Effekt bedeutet, regelmäßig einen festen Betrag zu investieren, egal welcher Kurs."},
                {"heading": "Glättet das Timing", "body": "Du kaufst mehr Anteile, wenn die Kurse niedrig sind, und weniger, wenn sie hoch sind – so mittelst du deine Kosten über die Zeit."},
                {"heading": "Besser als raten", "body": "Es nimmt den Stress, den Markt perfekt timen zu wollen, was selbst Profis selten gut gelingt."}],
            "questions": [
                {"q": "Der Cost-Average-Effekt investiert…", "options": ["einen festen Betrag nach Plan", "alles auf einmal am Höchststand", "nur wenn man Angst hat", "nie"], "explain": "Feste Beträge in regelmäßigen Abständen."},
                {"q": "Bei niedrigen Kursen kauft ein fester Betrag…", "options": ["weniger Anteile", "mehr Anteile", "keine Anteile", "nur Anleihen"], "explain": "Niedrigere Kurse kaufen mehr Anteile."},
                {"q": "Ein wesentlicher Vorteil ist…", "options": ["den Timing-Stress zu beseitigen", "garantierter Gewinn", "alle Steuern zu vermeiden", "das Geld monatlich zu verdoppeln"], "explain": "Es erspart das Timen des Marktes."}]},
        "l15": {"title": "Langfristiges Denken",
            "cards": [
                {"heading": "Zinseszins ist magisch", "body": "Reinvestierte Gewinne erwirtschaften eigene Gewinne. Über Jahrzehnte kann dieser Schneeball überraschend groß werden."},
                {"heading": "Kurs halten", "body": "Panikverkäufe in Abschwüngen zementieren Verluste. Die Geschichte zeigt, dass Märkte über lange Zeiträume nach oben tendierten."},
                {"heading": "Zeit im Markt", "body": "„Zeit im Markt schlägt das Timing des Marktes.“ Beständigkeit gewinnt meist gegen cleveres Raten."}],
            "questions": [
                {"q": "Zinseszins bedeutet…", "options": ["Gewinne, die eigene Gewinne erwirtschaften", "langsam Geld zu verlieren", "mehr Steuern zu zahlen", "alles zu verkaufen"], "explain": "Reinvestierte Gewinne verzinsen sich über die Zeit."},
                {"q": "Panikverkäufe in einem Abschwung neigen dazu…", "options": ["Verluste zu zementieren", "Gewinne zu garantieren", "den Markt anzuhalten", "Dividenden zu erhöhen"], "explain": "Tief zu verkaufen zementiert Verluste."},
                {"q": "Das Sprichwort lautet: Zeit im Markt schlägt…", "options": ["das Timing des Marktes", "das Sparen", "das Lesen von Charts", "das Diversifizieren"], "explain": "Beständigkeit schlägt den Versuch, Hoch- und Tiefpunkte zu timen."}]},
    },
    "es": {
        "l1": {"title": "¿Qué es una acción?",
            "cards": [
                {"heading": "Una parte de la propiedad", "body": "Una acción es una pequeña porción de propiedad de una empresa. Compra una acción y literalmente posees un trozo de ese negocio."},
                {"heading": "Por qué las empresas venden acciones", "body": "Las empresas venden acciones para conseguir dinero para crecer —construir fábricas, contratar personal o lanzar productos— sin endeudarse."},
                {"heading": "Eres accionista", "body": "Como accionista puedes ganar si la empresa aumenta de valor y, a veces, recibir una parte de los beneficios llamada dividendo."}],
            "questions": [
                {"q": "¿Qué representa poseer una acción?", "options": ["Un préstamo a la empresa", "Una parte de la propiedad de la empresa", "Un salario mensual garantizado", "Un bono del Estado"], "explain": "Una acción es propiedad parcial de una empresa."},
                {"q": "¿Por qué emiten acciones las empresas?", "options": ["Para conseguir dinero para crecer", "Para pagar impuestos", "Para no fabricar productos", "Para reducir su valor"], "explain": "Emitir acciones consigue capital sin pedir préstamos."},
                {"q": "A quien posee acciones se le llama…", "options": ["Prestamista", "Accionista", "Cliente", "Auditor"], "explain": "Los dueños de acciones son accionistas."}]},
        "l2": {"title": "Las bolsas de valores",
            "cards": [
                {"heading": "El mercado", "body": "Una bolsa de valores es un mercado donde compradores y vendedores negocian acciones. La NYSE y el Nasdaq están entre las mayores."},
                {"heading": "Emparejar órdenes", "body": "Las bolsas emparejan órdenes de compra y venta y publican el último precio que todos pueden ver, manteniendo la negociación justa y transparente."},
                {"heading": "Símbolos de cotización", "body": "Cada empresa recibe un símbolo corto —AAPL para Apple, TSLA para Tesla— para buscar y negociar la acción rápidamente."}],
            "questions": [
                {"q": "¿Qué es una bolsa de valores?", "options": ["La caja fuerte de un banco", "Un mercado para negociar acciones", "Un tipo de impuesto", "El almacén de una empresa"], "explain": "Las bolsas son mercados que emparejan compradores y vendedores."},
                {"q": "AAPL es el símbolo de…", "options": ["Amazon", "Apple", "Alphabet", "AMD"], "explain": "AAPL representa a Apple Inc."},
                {"q": "¿Cuál es una gran bolsa de EE. UU.?", "options": ["Nasdaq", "FIFA", "NASA", "IKEA"], "explain": "El Nasdaq es una gran bolsa, junto con la NYSE."}]},
        "l3": {"title": "Toros contra osos",
            "cards": [
                {"heading": "Mercado alcista", "body": "Un mercado alcista ocurre cuando los precios suben y el optimismo es alto. Piensa en un toro clavando los cuernos hacia arriba."},
                {"heading": "Mercado bajista", "body": "Un mercado bajista es una caída prolongada del 20 % o más, con pesimismo. Imagina a un oso lanzando su zarpa hacia abajo."},
                {"heading": "El ánimo mueve los mercados", "body": "Los precios reflejan cuán esperanzados o temerosos se sienten los inversores sobre el futuro, no solo los hechos de hoy."}],
            "questions": [
                {"q": "Un mercado que sube y es optimista se llama…", "options": ["Mercado bajista", "Mercado alcista", "Mercado plano", "Mercado muerto"], "explain": "Los toros embisten hacia arriba: precios en alza."},
                {"q": "Un mercado bajista suele significar que los precios…", "options": ["suben con fuerza", "se quedan exactamente planos", "caen de forma significativa", "se eliminan"], "explain": "Los mercados bajistas son caídas prolongadas del 20 %+."},
                {"q": "El sentimiento del mercado se refiere a…", "options": ["el ánimo y las expectativas de los inversores", "la temperatura del edificio", "la nómina de la empresa", "los tipos impositivos"], "explain": "El sentimiento es el ánimo colectivo de los inversores."}]},
        "l4": {"title": "Qué mueve los precios",
            "cards": [
                {"heading": "Oferta y demanda", "body": "Si más gente quiere comprar una acción que venderla, el precio sube. Si más quieren vender, baja."},
                {"heading": "Noticias y resultados", "body": "Buenos beneficios, nuevos productos o buenas noticias atraen compradores. Las malas noticias o resultados débiles empujan los precios a la baja."},
                {"heading": "Todo el mercado", "body": "Los tipos de interés, la economía y los eventos globales pueden mover casi todas las acciones a la vez."}],
            "questions": [
                {"q": "Si la demanda de una acción supera la oferta, el precio tiende a…", "options": ["caer", "subir", "congelarse", "desaparecer"], "explain": "Más compradores que vendedores empujan los precios al alza."},
                {"q": "¿Qué suele impulsar el precio de una acción?", "options": ["Un informe de resultados sólido", "La retirada de un producto", "Perder un juicio", "Ventas en caída"], "explain": "Los buenos resultados atraen compradores."},
                {"q": "¿Qué puede mover casi todas las acciones a la vez?", "options": ["La opinión de un solo cliente", "Cambios en los tipos de interés", "Un tuit sin alcance", "El logo de la empresa"], "explain": "Los factores macro como los tipos afectan a todo el mercado."}]},
        "l5": {"title": "Dividendos",
            "cards": [
                {"heading": "Repartir el beneficio", "body": "Un dividendo es un pago en efectivo que algunas empresas envían a los accionistas de sus beneficios, a menudo cada trimestre."},
                {"heading": "Rentabilidad por dividendo", "body": "Rentabilidad = dividendo anual ÷ precio de la acción. Un dividendo de 2 $ en una acción de 100 $ es un 2 %."},
                {"heading": "No todas pagan", "body": "Las empresas de rápido crecimiento suelen reinvertir los beneficios en vez de pagar dividendos, buscando un mayor crecimiento futuro."}],
            "questions": [
                {"q": "Un dividendo es…", "options": ["una multa", "una parte de los beneficios pagada a los dueños", "un tipo de préstamo", "un impuesto de negociación"], "explain": "Los dividendos reparten beneficios a los accionistas."},
                {"q": "Un dividendo anual de 4 $ en una acción de 100 $ es una rentabilidad del…", "options": ["0,4 %", "4 %", "40 %", "14 %"], "explain": "4 ÷ 100 = 4 %."},
                {"q": "Las empresas de crecimiento suelen…", "options": ["reinvertir beneficios en vez de pagar dividendos", "pagar siempre enormes dividendos", "no tener nunca beneficios", "pagar dividendos a diario"], "explain": "Reinvierten para impulsar el crecimiento."}]},
        "l6": {"title": "Riesgo y rentabilidad",
            "cards": [
                {"heading": "El equilibrio", "body": "Una mayor rentabilidad potencial suele venir con mayor riesgo. Los activos más seguros tienden a crecer más despacio."},
                {"heading": "Volatilidad", "body": "La volatilidad es cuánto oscila un precio arriba y abajo. Alta volatilidad significa movimientos mayores y más rápidos."},
                {"heading": "Horizonte temporal", "body": "Cuanto más tiempo puedas mantener la inversión, más se suavizan las oscilaciones a corto plazo."}],
            "questions": [
                {"q": "Una mayor rentabilidad potencial suele significar…", "options": ["menor riesgo", "mayor riesgo", "ningún riesgo", "beneficio garantizado"], "explain": "El riesgo y la recompensa van juntos."},
                {"q": "La volatilidad mide…", "options": ["la antigüedad de la empresa", "el tamaño de las oscilaciones del precio", "el número de empleados", "las fechas de dividendos"], "explain": "La volatilidad es el tamaño de las oscilaciones del precio."},
                {"q": "Un horizonte temporal más largo tiende a…", "options": ["amplificar las oscilaciones diarias para siempre", "suavizar las oscilaciones a corto plazo", "garantizar pérdidas", "eliminar todo el riesgo"], "explain": "El tiempo ayuda a suavizar la volatilidad."}]},
        "l7": {"title": "Índices de mercado",
            "cards": [
                {"heading": "Un marcador del mercado", "body": "Un índice sigue a un grupo de acciones para mostrar cómo va un mercado en conjunto, como un marcador."},
                {"heading": "Índices famosos", "body": "El S&P 500 sigue a 500 grandes empresas de EE. UU. El Nasdaq-100 es muy tecnológico. El Dow sigue a 30 grandes nombres."},
                {"heading": "Por qué importan", "body": "Los índices son referencias. Los inversores comparan sus rentabilidades con ellos para ver si superan al mercado."}],
            "questions": [
                {"q": "Un índice bursátil se describe mejor como…", "options": ["una sola empresa", "un marcador de un grupo de acciones", "una cuenta bancaria", "un formulario de impuestos"], "explain": "Los índices resumen un grupo de acciones."},
                {"q": "El S&P 500 sigue aproximadamente a…", "options": ["5 empresas", "50 empresas", "500 grandes empresas de EE. UU.", "5000 empresas"], "explain": "Sigue a 500 grandes firmas de EE. UU."},
                {"q": "Los inversores usan los índices como…", "options": ["referencias para comparar rentabilidades", "recetas de cocina", "contratos legales", "contraseñas"], "explain": "Los índices son referencias de rendimiento."}]},
        "l8": {"title": "Tipos de órdenes",
            "cards": [
                {"heading": "Orden de mercado", "body": "Una orden de mercado compra o vende de inmediato al mejor precio disponible. Rápida, pero el precio exacto no está garantizado."},
                {"heading": "Orden limitada", "body": "Una orden limitada solo se ejecuta a tu precio elegido o mejor. Controlas el precio, pero puede no ejecutarse."},
                {"heading": "Orden stop", "body": "Una orden stop activa una operación al alcanzarse un nivel de precio, a menudo usada para limitar pérdidas."}],
            "questions": [
                {"q": "Una orden de mercado prioriza…", "options": ["el precio exacto", "la velocidad de ejecución", "evitar operaciones", "los dividendos"], "explain": "Las órdenes de mercado se ejecutan rápido al mejor precio disponible."},
                {"q": "Una orden limitada te permite…", "options": ["fijar el precio que aceptarás", "saltarte la bolsa", "garantizar la ejecución", "evitar todas las comisiones"], "explain": "Las órdenes limitadas controlan el precio de ejecución."},
                {"q": "Una orden stop se usa a menudo para…", "options": ["limitar pérdidas potenciales", "pagar dividendos", "registrar una empresa", "aumentar la volatilidad"], "explain": "Los stops ayudan a limitar pérdidas."}]},
        "l9": {"title": "Leer un gráfico",
            "cards": [
                {"heading": "Precio en el tiempo", "body": "Un gráfico traza el precio en el eje vertical y el tiempo abajo, mostrando la historia de los movimientos de una acción."},
                {"heading": "Tendencias", "body": "Una tendencia alcista forma máximos y mínimos más altos. Una tendencia bajista forma máximos y mínimos más bajos."},
                {"heading": "Volumen", "body": "El volumen muestra cuántas acciones se negociaron. Los grandes movimientos con alto volumen se consideran más significativos."}],
            "questions": [
                {"q": "En un gráfico estándar, el tiempo se muestra en el…", "options": ["eje vertical", "eje horizontal", "logo de la empresa", "símbolo"], "explain": "El tiempo va a lo largo del eje horizontal."},
                {"q": "Una tendencia alcista es una serie de…", "options": ["máximos y mínimos más bajos", "máximos y mínimos más altos", "solo líneas planas", "puntos aleatorios"], "explain": "Las tendencias alcistas suben con máximos y mínimos más altos."},
                {"q": "El volumen de negociación mide…", "options": ["las acciones negociadas", "la antigüedad de la empresa", "el tamaño del dividendo", "el salario del CEO"], "explain": "El volumen es el número de acciones negociadas."}]},
        "l10": {"title": "Beneficios e ingresos",
            "cards": [
                {"heading": "Ingresos vs. beneficio", "body": "Los ingresos son todo el dinero que entra. El beneficio es lo que queda tras pagar todos los costes."},
                {"heading": "Temporada de resultados", "body": "Cada trimestre las empresas publican resultados. Superar las expectativas suele subir la acción; no cumplirlas puede hundirla."},
                {"heading": "BPA", "body": "El beneficio por acción (BPA) es el beneficio dividido por el número de acciones: una lectura rápida de la rentabilidad por acción."}],
            "questions": [
                {"q": "El beneficio son los ingresos menos…", "options": ["nada", "todos los costes y gastos", "solo los dividendos", "el precio de la acción"], "explain": "El beneficio es lo que queda tras los costes."},
                {"q": "BPA significa…", "options": ["Beneficio Por Acción", "Balance Positivo Anual", "Escala de Precio de Capital", "Sistema de Prioridad de Bolsa"], "explain": "BPA = Beneficio Por Acción."},
                {"q": "Superar las expectativas de resultados suele…", "options": ["subir la acción", "excluir a la empresa de la bolsa", "cancelar dividendos", "no tener nunca efecto"], "explain": "Superar tiende a empujar los precios al alza."}]},
        "l11": {"title": "El PER (P/E)",
            "cards": [
                {"heading": "Precio-beneficio", "body": "El PER = precio de la acción ÷ beneficio por acción. Muestra cuánto pagan los inversores por 1 $ de beneficio."},
                {"heading": "Alto vs. bajo", "body": "Un PER alto puede significar altas expectativas de crecimiento, o una acción cara. Un PER bajo puede indicar valor o problemas."},
                {"heading": "Comparar con justicia", "body": "El PER es más útil al comparar empresas similares del mismo sector."}],
            "questions": [
                {"q": "El PER compara el precio con…", "options": ["los ingresos", "el beneficio por acción", "los dividendos", "el volumen"], "explain": "PER = precio ÷ BPA."},
                {"q": "Un PER muy alto suele reflejar…", "options": ["altas expectativas de crecimiento", "interés cero", "un desplome garantizado", "nunca beneficios"], "explain": "Un PER alto implica expectativas de crecimiento."},
                {"q": "El PER es más significativo cuando…", "options": ["se comparan empresas similares", "se compara un banco con una panadería", "se ignora el sector", "se aplica a números al azar"], "explain": "Compara dentro del mismo sector."}]},
        "l12": {"title": "Capitalización de mercado",
            "cards": [
                {"heading": "Tamaño de la empresa", "body": "La capitalización de mercado = precio de la acción × total de acciones. Es la etiqueta de precio del mercado para toda la empresa."},
                {"heading": "Clases por tamaño", "body": "Gran capitalización (enorme, estable), mediana (en crecimiento) y pequeña (más pequeña, más arriesgada, mayor potencial de crecimiento)."},
                {"heading": "Precio ≠ tamaño", "body": "Una acción de 500 $ no es automáticamente más grande que una de 10 $: depende de cuántas acciones existan."}],
            "questions": [
                {"q": "La capitalización de mercado es el precio de la acción por…", "options": ["el total de acciones en circulación", "el PER", "los ingresos", "la rentabilidad por dividendo"], "explain": "Capitalización = precio × acciones."},
                {"q": "Las empresas de gran capitalización son en general…", "options": ["diminutas y arriesgadas", "enormes y más estables", "siempre no rentables", "solo privadas"], "explain": "Las de gran capitalización son grandes y relativamente estables."},
                {"q": "Un precio de acción más alto por sí solo significa que la empresa es más grande. ¿Verdadero o falso?", "options": ["Verdadero", "Falso"], "explain": "El tamaño también depende de las acciones en circulación."}]},
        "l13": {"title": "Diversificación",
            "cards": [
                {"heading": "No pongas todos los huevos en una cesta", "body": "Repartir el dinero entre muchas acciones y sectores reduce el daño si una sola cae."},
                {"heading": "Los fondos lo facilitan", "body": "Los fondos indexados y los ETF agrupan cientos de acciones en una sola compra: diversificación instantánea."},
                {"heading": "Menos riesgo, camino más estable", "body": "La diversificación no elimina todo el riesgo, pero suaviza la rentabilidad y protege ante desastres de una sola empresa."}],
            "questions": [
                {"q": "Diversificar significa…", "options": ["comprar una sola acción", "repartir las inversiones entre muchas", "cronometrar el mercado a diario", "evitar todas las acciones"], "explain": "Reparte el riesgo entre muchas posiciones."},
                {"q": "Una forma fácil de diversificar es comprar…", "options": ["un fondo indexado o ETF", "una sola acción", "solo la acción de tu empleador", "boletos de lotería"], "explain": "Los ETF agrupan muchas acciones a la vez."},
                {"q": "La diversificación reduce sobre todo…", "options": ["el riesgo de una sola empresa", "tu edad", "el horario de negociación", "la longitud del símbolo"], "explain": "Amortigua los desastres de una sola empresa."}]},
        "l14": {"title": "Promediado del coste (DCA)",
            "cards": [
                {"heading": "Invertir con un plan", "body": "El promediado del coste consiste en invertir una cantidad fija con regularidad, sin importar el precio."},
                {"heading": "Suaviza el momento", "body": "Compras más participaciones cuando los precios están bajos y menos cuando están altos, promediando tu coste con el tiempo."},
                {"heading": "Mejor que adivinar", "body": "Elimina el estrés de intentar cronometrar el mercado a la perfección, algo que incluso los profesionales rara vez logran bien."}],
            "questions": [
                {"q": "El promediado del coste invierte…", "options": ["una cantidad fija con un plan", "todo de golpe en el máximo", "solo cuando hay miedo", "nunca"], "explain": "Cantidades fijas a intervalos regulares."},
                {"q": "Cuando los precios están bajos, una cantidad fija compra…", "options": ["menos participaciones", "más participaciones", "ninguna participación", "solo bonos"], "explain": "Precios más bajos compran más participaciones."},
                {"q": "Un beneficio clave es…", "options": ["eliminar el estrés de cronometrar el mercado", "garantizar beneficios", "evitar todos los impuestos", "duplicar el dinero cada mes"], "explain": "Evita la necesidad de cronometrar el mercado."}]},
        "l15": {"title": "Mentalidad a largo plazo",
            "cards": [
                {"heading": "El interés compuesto es mágico", "body": "Las ganancias reinvertidas generan sus propias ganancias. A lo largo de décadas, esta bola de nieve puede crecer sorprendentemente."},
                {"heading": "Mantén el rumbo", "body": "Vender por pánico en las caídas fija las pérdidas. La historia muestra que los mercados han tendido al alza en periodos largos."},
                {"heading": "Tiempo en el mercado", "body": "«El tiempo en el mercado supera al cronometraje del mercado.» La constancia suele ganar frente a las conjeturas ingeniosas."}],
            "questions": [
                {"q": "El interés compuesto significa…", "options": ["ganancias que generan sus propias ganancias", "perder dinero despacio", "pagar más impuestos", "venderlo todo"], "explain": "Las ganancias reinvertidas se componen con el tiempo."},
                {"q": "Vender por pánico en una caída tiende a…", "options": ["fijar las pérdidas", "garantizar ganancias", "pausar el mercado", "subir los dividendos"], "explain": "Vender barato fija las pérdidas."},
                {"q": "El dicho dice: el tiempo en el mercado supera a…", "options": ["cronometrar el mercado", "ahorrar dinero", "leer gráficos", "diversificar"], "explain": "La constancia supera intentar acertar máximos y mínimos."}]},
    },
}

STOCK_T = {
    "de": {
        "AAPL": "Stellt das iPhone, den Mac und Dienste wie den App Store her – eines der wertvollsten Unternehmen der Welt.",
        "MSFT": "Verkauft Windows, Office und die Azure-Cloud und ist eine treibende Kraft bei Unternehmens-KI.",
        "GOOGL": "Mutterkonzern von Google Suche und YouTube; verdient das meiste Geld mit Online-Werbung.",
        "AMZN": "Der E-Commerce-Riese, der auch AWS betreibt, die größte Cloud-Plattform der Welt.",
        "NVDA": "Entwickelt die GPUs, die Gaming und den KI-Boom antreiben – Chips, die derzeit jeder will.",
        "META": "Besitzt Facebook, Instagram und WhatsApp und finanziert große KI- und Metaverse-Wetten mit Werbeeinnahmen.",
        "TSLA": "Führender E-Auto-Hersteller, der auch an Batterien, Solar und autonomem Fahren arbeitet.",
        "F": "Hundertjähriger Autobauer, bekannt für Trucks wie den F-150, jetzt mit Vorstoß in E-Autos.",
        "JPM": "Die größte US-Bank, von Girokonten bis zu Wall-Street-Deals.",
        "V": "Betreibt das Zahlungsnetzwerk hinter Milliarden Kartenzahlungen und nimmt bei jeder eine kleine Gebühr.",
        "KO": "Verkauft weltweit Erfrischungsgetränke und ist eine klassische, stetige Dividendenaktie.",
        "MCD": "Globale Fast-Food-Kette, die stark über Franchising und Immobilien verdient.",
        "DIS": "Unterhaltungsriese hinter Freizeitparks, Marvel, Star Wars und dem Streaming-Dienst Disney+.",
        "NFLX": "Der Streaming-Pionier mit Hunderten Millionen Abonnenten weltweit.",
        "SPY": "Ein einzelner Fonds, der 500 Top-US-Unternehmen abbildet – sofortige Diversifikation in einem Kauf.",
        "QQQ": "Bildet 100 der größten Nicht-Finanz-Nasdaq-Namen ab – sehr techlastiges Engagement.",
    },
    "es": {
        "AAPL": "Fabrica el iPhone, el Mac y servicios como la App Store: una de las empresas más valiosas del mundo.",
        "MSFT": "Vende Windows, Office y la nube Azure, y es una gran fuerza en la IA empresarial.",
        "GOOGL": "Matriz de Google y YouTube; gana la mayor parte de su dinero con la publicidad online.",
        "AMZN": "El gigante del comercio electrónico que también opera AWS, la mayor plataforma de nube del mundo.",
        "NVDA": "Diseña las GPU que impulsan los videojuegos y el auge de la IA: los chips que todos quieren ahora.",
        "META": "Dueña de Facebook, Instagram y WhatsApp; financia grandes apuestas de IA y metaverso con ingresos publicitarios.",
        "TSLA": "Fabricante líder de coches eléctricos que también trabaja en baterías, solar y conducción autónoma.",
        "F": "Fabricante centenario famoso por camionetas como la F-150, ahora impulsando los eléctricos.",
        "JPM": "El mayor banco de EE. UU., desde cuentas corrientes hasta grandes operaciones de Wall Street.",
        "V": "Opera la red de pagos tras miles de millones de pagos con tarjeta, cobrando una pequeña comisión en cada uno.",
        "KO": "Vende refrescos en todo el mundo y es una clásica acción estable de dividendos.",
        "MCD": "Cadena global de comida rápida que gana mucho con las franquicias y los inmuebles.",
        "DIS": "Potencia del entretenimiento tras los parques temáticos, Marvel, Star Wars y el streaming Disney+.",
        "NFLX": "El pionero del streaming con cientos de millones de suscriptores en todo el mundo.",
        "SPY": "Un solo fondo que sigue a 500 grandes empresas de EE. UU.: diversificación instantánea en una compra.",
        "QQQ": "Sigue a 100 de los mayores nombres no financieros del Nasdaq: exposición muy tecnológica.",
    },
}

SUPPORTED_LANGS = {"en", "de", "es"}


def norm_lang(lang):
    if not lang:
        return "en"
    lang = lang.lower().split("-")[0]
    return lang if lang in SUPPORTED_LANGS else "en"
