# Lokale Frontend-Abhängigkeiten

`chart.umd.min.js` wird beim Docker-Image-Build automatisch als Chart.js 4.5.1
heruntergeladen und anschließend lokal über `/static/vendor/chart.umd.min.js` ausgeliefert.

Dadurch benötigt Fintra im laufenden Betrieb keine Verbindung zu jsDelivr oder einem
anderen CDN. Nur für einen komplett neuen Docker-Build muss die Datei einmalig
erreichbar sein.

Quelle: Chart.js 4.5.1, MIT-Lizenz.
