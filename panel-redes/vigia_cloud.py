import json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime

DATA_PATH = pathlib.Path(__file__).resolve().parent / "data.json"

DOMINIOS_BLOQUEADOS = {
    "wradio", "w radio", "semana", "el colombiano", "elcolombiano",
    "el tiempo", "eltiempo", "la republica", "larepublica", "portafolio",
    "caracol", "blu radio", "bluradio", "rcn", "noticias rcn", "la fm", "lafm",
    "pulzo", "infobae", "el nuevo siglo", "elnuevosiglo", "las2orillas",
    "revista alternativa", "cambio16", "kienyke", "valora analitik", "forbes",
    "el heraldo", "el pais", "elpais.com.co", "vanguardia", "el universal"
}

RADARES = [
    ("Facebook", "NORMATIVA LABORAL", "(site:ambitojuridico.com OR site:corteconstitucional.gov.co OR site:cortesuprema.gov.co OR site:mintrabajo.gov.co OR site:gerencie.com OR site:actualicese.com) (laboral OR despido OR salario OR prima OR pension OR incapacidad OR ARL)"),
    ("Facebook", "ACADEMIA Y DERECHOS", "(site:dejusticia.org OR site:razonpublica.com OR site:revistapacto.com OR site:voragine.co OR site:cuestionpublica.com OR site:cambiocolombia.com OR site:elespectador.com) (trabajadores OR laboral OR pensiones OR EPS OR derechos)"),
    ("Instagram", "CONTRATOS Y CONSUMO", "(site:ambitojuridico.com OR site:sic.gov.co OR site:superfinanciera.gov.co OR site:gerencie.com) (consumidor OR contrato OR arriendo OR banco OR garantia)"),
    ("TikTok", "JURISPRUDENCIA", "(site:corteconstitucional.gov.co OR site:cortesuprema.gov.co OR site:ambitojuridico.com OR site:dejusticia.org) (tutela OR sentencia OR fallo OR multa OR datos personales)"),
]


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()


def _bloq(f, t, u):
    b = f"{f} {t} {u}".lower()
    return any(x in b for x in DOMINIOS_BLOQUEADOS)


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    exist = {_norm(i.get("titulo", "")) for i in data.get("ideas", [])}
    nuevas = []
    for red, tag, q in RADARES:
        url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=es-419&gl=CO&ceid=CO:es-419"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            root = ET.fromstring(urllib.request.urlopen(req, timeout=12).read())
            for it in root.findall(".//item")[:5]:
                tit = re.sub(r"\s*-\s*[^-]+$", "", (it.findtext("title") or "").strip()).strip()
                lnk = (it.findtext("link") or "").strip()
                fnt = (it.findtext("source") or "Fuente Jurídica").strip()
                if not tit or _bloq(fnt, tit, lnk) or _norm(tit) in exist:
                    continue
                nuevas.append({
                    "id": f"cloud-{int(datetime.now().timestamp())}-{len(nuevas)+1}",
                    "fecha_detectada": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "red": red,
                    "tag": tag,
                    "titulo": tit,
                    "gancho": f"Atención a este criterio jurídico sobre {tit.lower()}, porque puede impactar tus derechos y tu bolsillo en Colombia",
                    "fuente": fnt,
                    "url": lnk,
                    "puntaje_viral": 85,
                    "estado": "PENDIENTE",
                    "origen": "Vigia Nube 24/7",
                })
                exist.add(_norm(tit))
                if len(nuevas) >= 6:
                    break
        except Exception:
            continue
    data["ideas"] = (nuevas + data.get("ideas", []))[:60]
    data["ultima_corrida_vigia"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S (Nube)")
    data["generado_web"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("CLOUD_VIGIA_OK", len(nuevas), "nuevas")


if __name__ == "__main__":
    main()
