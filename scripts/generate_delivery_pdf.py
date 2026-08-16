#!/usr/bin/env python3
"""Genera el plan académico paginado de cinco hojas."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "plan-migracion-sap-analytics-aws.pdf"
BLUE = colors.HexColor("#163B65")
CYAN = colors.HexColor("#1596B8")
LIGHT = colors.HexColor("#EAF2F8")
INK = colors.HexColor("#1F2933")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#52606D"))
    canvas.drawString(18 * mm, 9 * mm, "Proyecto final - Migracion de analitica SAP ECC hacia AWS")
    canvas.drawRightString(192 * mm, 9 * mm, f"Pagina {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "PageTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=22, leading=26, textColor=BLUE, spaceAfter=8 * mm,
))
styles.add(ParagraphStyle(
    "Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=13, leading=16, textColor=BLUE, spaceBefore=3 * mm,
    spaceAfter=2 * mm, keepWithNext=0,
))
styles.add(ParagraphStyle(
    "BodySmall", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.3, leading=12.4, textColor=INK, spaceAfter=2.5 * mm,
))
styles.add(ParagraphStyle(
    "Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=10, leading=13, textColor=BLUE, backColor=LIGHT,
    borderPadding=8, spaceAfter=4 * mm,
))
styles.add(ParagraphStyle(
    "TableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=8.5, leading=10.5, textColor=colors.white,
))
styles.add(ParagraphStyle(
    "Cover", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=25, leading=30, alignment=TA_CENTER, textColor=BLUE,
))


def p(text, style="BodySmall"):
    return Paragraph(text, styles[style])


def table(rows, widths, header=True, font_size=8.2):
    data = []
    for row_index, row in enumerate(rows):
        style = "TableHeader" if header and row_index == 0 else "BodySmall"
        data.append([[p(str(cell), style)][0] for cell in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BCCCDC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
    t.setStyle(TableStyle(commands))
    return t


def bullets(items):
    return [p(f"• {item}") for item in items]


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Plan de migracion de analitica SAP ECC hacia AWS",
        author="Diego Lagre",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="all", frames=[frame], onPage=footer))
    story = []

    # Hoja 1
    story += [Spacer(1, 25 * mm), p("PROYECTO FINAL - CLOUD COMPUTING", "Callout")]
    story += [p("Migracion de la plataforma analitica SAP ECC hacia AWS", "Cover")]
    story += [Spacer(1, 8 * mm), p("Autor: Diego Lagre · Entrega individual", "Callout")]
    story += [p("Hoja 1 - Caso, alcance y objetivos", "PageTitle")]
    story += [p("Problema", "Section"), p(
        "La organizacion mantiene SAP ECC on-premise y necesita desacoplar el analisis de "
        "rentabilidad CO-PA de la plataforma transaccional. El universo de referencia es "
        "una tabla CE1xxxx de aproximadamente 45 millones de registros. SAP BW no forma "
        "parte del flujo elegido."
    )]
    story += [p("Alcance", "Section"), p(
        "Se migra la extraccion, almacenamiento, transformacion y consumo analitico. SAP "
        "ECC permanece on-premise. La demostracion usa CSV sintetico para proteger toda "
        "informacion productiva. SAP SLT DMIS 2018 se representa mediante un simulador "
        "idempotente y en produccion publica el origen mediante ODP/OData."
    )]
    story += [p("Objetivos SMART", "Section")]
    story += bullets([
        "Completar el corte en diez semanas, con interrupcion de reportes menor a cuatro horas.",
        "Procesar carga inicial y deltas sin perdidas ni duplicados y conciliar diferencias menores o iguales a 0,1 %.",
        "Mantener RDS privado y habilitar usuarios internos por VPN y Power BI mediante gateway TLS.",
        "Estabilizar durante cinco dias habiles sin incidentes criticos abiertos.",
        "Mantener el escenario base alrededor de USD 780,44 mensuales antes de descuentos e impuestos.",
    ])
    story += [p("Resultado demostrable", "Section"), p(
        "Un unico recorrido crea cinco servicios AWS en LocalStack, procesa 1.000 registros "
        "iniciales y 50 incrementales, carga PostgreSQL y termina con 13 controles OK, cero "
        "advertencias y trece pruebas automatizadas aprobadas."
    ), PageBreak()]

    # Hoja 2
    story += [p("Hoja 2 - Arquitectura y servicios", "PageTitle")]
    story += [p(
        "Flujo: SAP ECC -> SAP SLT -> ODP/OData -> VPN -> AppFlow -> S3 Landing -> "
        "EC2 Auto Scaling ETL -> S3 Curated -> RDS PostgreSQL -> usuarios y Power BI Gateway.",
        "Callout",
    )]
    rows = [["Servicio evaluado", "Funcion", "Justificacion"]] + [
        ["1. IAM", "Identidades y minimo privilegio", "Evita claves embebidas"],
        ["2. Amazon VPC", "Red y subredes privadas", "Aisla ETL y RDS"],
        ["3. Amazon S3", "Zonas Landing y Curated", "Permite trazabilidad y reproceso"],
        ["4. Amazon AppFlow", "Ingesta OData incremental", "Reduce conector propio"],
        ["5. Amazon EC2", "Workers ETL", "Admite procesos y librerias extensos"],
        ["6. Amazon EBS", "Disco de workers y gateways", "Persistencia de bloque administrada"],
        ["7. EC2 Auto Scaling", "Escalado de workers", "Absorbe carga inicial y fallos"],
        ["8. Amazon RDS", "Data Warehouse PostgreSQL", "Menor complejidad que Redshift"],
        ["9. Secrets Manager", "Credenciales administradas", "Evita secretos en Terraform"],
        ["10. CloudWatch", "Logs, metricas y alarmas", "Habilita operacion observable"],
    ]
    story += [table(rows, [32 * mm, 55 * mm, 87 * mm])]
    story += [Spacer(1, 4 * mm), p(
        "KMS, Site-to-Site VPN y backups son capacidades transversales de seguridad, "
        "conectividad y continuidad; no se contabilizan como servicios adicionales del "
        "nucleo evaluado.", "Callout"
    )]
    story += [p("Conectividad y consumo", "Section")]
    story += bullets([
        "Usuarios corporativos: red privada mediante Site-to-Site VPN; Direct Connect es evolucion futura.",
        "Power BI Service: clúster de dos gateways, TLS y usuario PostgreSQL de solo lectura.",
        "RDS no posee endpoint publico y solo acepta security groups aprobados.",
    ])
    story += [p("Alternativas descartadas", "Section"), p(
        "No se migra SAP ECC completo; no se usa BW como origen; Lambda se descarta para "
        "procesos extensos; Redshift no se justifica para el volumen inicial; Airbyte no "
        "reemplaza el patron solicitado y RDS nunca se expone directamente a Internet."
    ), PageBreak()]

    # Hoja 3
    story += [p("Hoja 3 - Dimensionamiento, seguridad y costos", "PageTitle")]
    sizing = [
        ["Componente", "Configuracion base"],
        ["AppFlow", "Incremental horario; historico particionado por ejercicio y periodo"],
        ["S3", "100 GiB iniciales; 200 GiB previstos en el primer año"],
        ["ETL", "m6i.large; min 1, deseado 1, max 4; EBS gp3 30 GB"],
        ["RDS", "db.m6g.large Multi-AZ; 100 GB gp3; maximo 200 GB"],
        ["Gateway BI", "Dos m6i.large Windows y 100 GB EBS en total"],
        ["Red", "VPN con dos tuneles; al menos 100 Mbit/s efectivos"],
    ]
    story += [table(sizing, [42 * mm, 132 * mm])]
    story += [p("Controles", "Section")]
    story += bullets([
        "Cifrado, bloqueo publico de S3, TLS y credenciales administradas.",
        "RDS Multi-AZ, backups por 14 dias, proteccion contra borrado y restauracion probada.",
        "IAM limita al ETL a Landing, Curated y sus secretos autorizados.",
        "CloudWatch alerta sobre delta detenida, saturacion, espacio y errores de carga.",
    ])
    costs = [
        ["Categoria", "Mensual"],
        ["Power BI Gateway en AWS", "USD 282,48"],
        ["RDS PostgreSQL Multi-AZ", "USD 298,14"],
        ["EC2 ETL y EBS", "USD 108,48"],
        ["VPN fuera del Calculator", "USD 36,50"],
        ["PrivateLink complementario", "USD 43,90"],
        ["S3, AppFlow, seguridad y monitoreo", "USD 10,94"],
        ["Total mensual / anual", "USD 780,44 / USD 9.365,28"],
    ]
    story += [p("Estimacion productiva", "Section"), table(costs, [115 * mm, 59 * mm])]
    story += [p(
        "Calculator informa USD 700,04. La VPN agrega USD 36,50 y los VPC endpoints "
        "privados USD 43,90 como suplementos trazables. S3 Gateway Endpoint no tiene cargo.", "Callout"
    ), PageBreak()]

    # Hoja 4
    story += [p("Hoja 4 - Cronograma, corte y continuidad", "PageTitle")]
    timeline = [
        ["Semanas", "Etapa", "Resultado"],
        ["1-2", "Preparacion", "Alcance, accesos, seguridad y conectividad aprobados"],
        ["2-4", "Construccion", "Infraestructura y publicacion ODP/OData listas"],
        ["4-7", "Pruebas", "Funcional, volumen, recuperacion y aceptacion BI"],
        ["7-8", "Ensayo", "Corte y reversa de punta a punta"],
        ["8-9", "Corte", "Historico, delta final, conciliacion y habilitacion"],
        ["9-10", "Hypercare", "Cinco dias sin incidentes criticos y transferencia"],
    ]
    story += [table(timeline, [24 * mm, 38 * mm, 112 * mm])]
    story += [p("Go/No-Go", "Section")]
    story += bullets([
        "Historico y delta conciliados; diferencias menores o iguales a 0,1 % y explicadas.",
        "Backup y restauracion probados; gateway, dataset y usuarios validados.",
        "Alarmas, responsables y plataforma anterior en modo consulta disponibles.",
    ])
    story += [p("Reversa", "Section"), p(
        "Se revierte ante diferencia no explicada superior a 0,1 %, delta detenida por mas "
        "de dos horas, consulta critica incorrecta o incidente grave de seguridad. La reversa "
        "reactiva el consumo anterior y conserva Landing y RDS para diagnostico."
    )]
    story += [p("Gestion del cambio", "Section")]
    change = [
        ["Momento", "Accion", "Evidencia"],
        ["Inicio", "Acordar alcance, RACI y audiencias", "Acta aprobada"],
        ["Pruebas", "Demo y validacion de usuarios clave", "Observaciones cerradas"],
        ["48 h antes", "Comunicar ventana, impacto y soporte", "Aviso enviado"],
        ["Corte", "Estado horario y decisiones", "Bitacora"],
        ["Hypercare", "Capacitacion y transferencia", "Aceptacion operativa"],
    ]
    story += [table(change, [28 * mm, 98 * mm, 48 * mm])]
    story += [p(
        "Cada rol operativo debe tener titular y suplente capacitados. La transferencia se "
        "acepta con runbooks, escalamiento, accesos, tablero de salud y cinco dias sin "
        "incidentes criticos.", "Callout"
    ), PageBreak()]

    # Hoja 5
    story += [p("Hoja 5 - Reproducibilidad y evidencias", "PageTitle")]
    story += [p("Demostracion con un comando", "Section"), p(
        "./scripts/presentation_demo.sh", "Callout"
    )]
    story += [p(
        "El bootstrap levanta LocalStack y PostgreSQL, materializa S3, IAM, VPC/EC2, "
        "Secrets Manager y CloudWatch Logs, genera CSV sintetico, simula SLT, ejecuta ETL "
        "y valida el modelo dimensional. Terraform conserva la arquitectura productiva."
    )]
    evidence = [
        ["Criterio", "Evidencia versionada"],
        ["Alcance y arquitectura", "docs/delivery-guide.md y docs/architecture.md"],
        ["SMART, Gantt y cutover", "docs/migration-plan.md"],
        ["Dimensionamiento", "docs/sizing.md e iac/"],
        ["Costos", "docs/cost-estimate.md y costs/aws-us-east-1.json"],
        ["Pricing Calculator", "PDF oficial, enlace compartido y conciliacion"],
        ["Cuatro o mas servicios", "compose.yaml y scripts/bootstrap_cloud.py"],
        ["Cultura y procesos", "docs/change-management.md"],
        ["Pruebas", "scripts/check.sh y tests/"],
    ]
    story += [p("Matriz de evidencia", "Section"), table(evidence, [52 * mm, 122 * mm])]
    story += [p("Pendientes externos antes de entregar", "Section")]
    story += [p(
        "• Confirmar us-east-1 como region definitiva.<br/>"
        "• Confirmar EntitySet OData de CE1xxxx, delta queue y Connector Profile para un piloto real.<br/>"
        "• Ensayar la defensa, backup, restauracion, corte y reversa."
    )]
    story += [p("Conclusion", "Section"), p(
        "El repositorio cubre alcance, arquitectura, tiempo, recursos, costos, diez servicios "
        "evaluados, codigo reproducible, seguridad y gestion del cambio. La estimacion oficial "
        "y la VPN complementaria quedan trazadas con sus fuentes y supuestos.", "Callout"
    )]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
