# Registro de decisiones de arquitectura

### 001 — Mantener SAP ERP on-premise

**Decisión:** migrar solamente la plataforma analítica.
**Contexto:** una migración completa de SAP excede el alcance.
**Alternativas:** migrar SAP completo o extraer desde SAP BW.
**Tradeoff:** se conserva dependencia híbrida, pero se reducen riesgo y costo.
**Resultado:** SAP ERP es el origen y SAP BW queda fuera del flujo.

### 002 — Utilizar SAP SLT para la extracción

**Decisión:** SAP SLT replica datos desde SAP ERP hacia la ingesta.
**Contexto:** se necesita una extracción controlada e incremental.
**Alternativas:** exportaciones manuales, jobs ABAP o extracción desde BW.
**Tradeoff:** SLT requiere operación on-premise, pero desacopla la extracción.
**Resultado:** localmente se representa con un script idempotente.

### 003 — Separar S3 Landing y Curated

**Decisión:** usar buckets separados para datos recibidos y validados.
**Contexto:** los originales deben preservarse para auditoría y reproceso.
**Alternativas:** un solo bucket o carga directa a RDS.
**Tradeoff:** más recursos, a cambio de trazabilidad y recuperación.
**Resultado:** el ETL lee Landing y escribe Curated con permisos mínimos.

### 004 — Usar PostgreSQL administrado como Data Warehouse

**Decisión:** utilizar Amazon RDS PostgreSQL para el modelo dimensional.
**Contexto:** el volumen inicial es moderado y se requiere una base administrada.
**Alternativas:** Redshift, Athena o PostgreSQL en EC2.
**Tradeoff:** menor escala que Redshift, con menor costo y complejidad inicial.
**Resultado:** PostgreSQL local representa RDS durante la demostración.

### 005 — Mantener RDS privado

**Decisión:** desplegar RDS sin acceso público.
**Contexto:** usuarios y SaaS deben consumir datos sin exponer la base.
**Alternativas:** endpoint público restringido o API pública intermedia.
**Tradeoff:** requiere conectividad privada o gateway, pero reduce riesgos.
**Resultado:** usuarios internos acceden por VPN/Direct Connect y Power BI por gateway y TLS.

### 006 — Reutilizar cloud-foundations-lab como base

**Decisión:** partir del código de `diegolagre/cloud-foundations-lab` para los componentes equivalentes.
**Contexto:** el laboratorio contiene patrones ya probados para Compose, LocalStack, Terraform, S3 y PostgreSQL.
**Alternativas:** implementar cada componente desde cero o incorporar otro framework.
**Tradeoff:** las adaptaciones deben respetar la estructura del laboratorio, pero se reducen errores y trabajo duplicado.
**Resultado:** los scripts SAP SLT/ETL reutilizarán `upload_to_object_storage.py`, `load_postgres.py`, `bootstrap.sh` y `check.sh`; la infraestructura partirá de `infra/terraform`.

### 007 — Usar AppFlow entre SLT/ODP y S3 en producción

**Decisión:** AppFlow consumirá el servicio OData generado sobre el proveedor ODP de SLT.
**Contexto:** AWS soporta SLT como proveedor ODP y el profesor recomendó evaluar AppFlow.
**Alternativas:** integrador propio, Airbyte o carga directa desde SLT.
**Tradeoff:** requiere SAP Gateway y OData compatibles, pero evita mantener un conector propio.
**Resultado:** Terraform incluye un flujo opcional SAPOData → S3, pendiente del `EntitySet` real.

### 008 — Ejecutar ETL en un Auto Scaling Group

**Decisión:** reemplazar la instancia EC2 única por workers definidos con Launch Template y Auto Scaling.
**Contexto:** una única instancia sería un punto de falla y limitaría el procesamiento de cargas.
**Alternativas:** EC2 única, Lambda, Glue o Airbyte.
**Tradeoff:** Auto Scaling agrega configuración, pero permite reemplazo automático y escalabilidad.
**Resultado:** el grupo mantiene entre cero y cuatro workers según el ambiente y escala por CPU.

### 009 — Administrar la credencial maestra de RDS con Secrets Manager

**Decisión:** permitir que RDS genere, almacene y rote la contraseña maestra.
**Contexto:** una contraseña ingresada como variable puede persistir en el estado de Terraform.
**Alternativas:** variable sensible, secreto creado manualmente o credenciales IAM para base de datos.
**Tradeoff:** aumenta la dependencia de Secrets Manager, pero elimina el manejo manual del secreto maestro.
**Resultado:** Terraform expone únicamente el ARN sensible del secreto; ETL y BI usarán usuarios separados.

### 010 — Utilizar una clave KMS de datos en producción

**Decisión:** cifrar S3 y RDS con una clave administrada por el proyecto y rotación habilitada.
**Contexto:** se necesita control explícito del ciclo de vida y los permisos de cifrado.
**Alternativas:** claves administradas por AWS o cifrado SSE-S3.
**Tradeoff:** la CMK agrega costo y responsabilidades de permisos, a cambio de mayor control y auditoría.
**Resultado:** la línea base KMS es opcional y sólo se habilita al desplegar sobre AWS real.

### 011 — Realizar un corte progresivo con reversa

**Decisión:** cargar el histórico antes del corte, procesar un delta final y habilitar primero un grupo piloto.
**Contexto:** el ERP continúa operativo y el cambio afecta la plataforma analítica, no las transacciones SAP.
**Alternativas:** corte directo para todos los usuarios o ejecución paralela indefinida.
**Tradeoff:** requiere conciliación y una semana de hypercare, pero reduce el impacto de resultados incorrectos.
**Resultado:** el cronograma contempla ensayo, Go/No-Go, corte menor a cuatro horas y condiciones explícitas de reversa.
