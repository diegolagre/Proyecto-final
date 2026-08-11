# Guion para la defensa

Duración sugerida: entre ocho y diez minutos, más preguntas. La presentación no
necesita leerse; cada diapositiva sostiene una idea y una evidencia.

## Antes de comenzar

1. Abrir `outputs/proyecto-final-sap-analytics-aws.pptx`.
2. Verificar que Docker Desktop esté iniciado.
3. Desde la raíz del repositorio, ejecutar `./scripts/bootstrap.sh`.
4. Mantener una terminal preparada con `./scripts/presentation_demo.sh`.
5. No mostrar `.env`, credenciales ni datos de un sistema productivo.

## Diapositiva 1 — SAP CO-PA: de ECC a AWS

**Tiempo:** 30 segundos.

> Este proyecto migra la plataforma analítica de CO-PA hacia AWS. No migramos
> SAP ECC: resolvemos un componente acotado, pero de punta a punta, con código,
> dimensionamiento, cronograma y costos.

Mensaje clave: es un plan de migración defendible, no solamente una demo local.

## Diapositiva 2 — La decisión

**Tiempo:** 50 segundos.

> SAP ECC y la operación transaccional permanecen on-premise. SAP SLT replica
> la tabla CO-PA y AWS recibe, transforma y sirve los datos. De esta manera
> desacoplamos reportes del ERP sin asumir el riesgo de migrar todo SAP.

Remarcar que SAP BW queda fuera del flujo de origen.

## Diapositiva 3 — Alcance CO-PA

**Tiempo:** 60 segundos.

> A la izquierda está lo que no cambia: ECC, CE1xxxx, SLT DMIS 2018 y la
> exposición ODP/OData. A la derecha está el componente migrado: AppFlow,
> Landing, ETL, Curated, PostgreSQL y consumo. El proyecto usa datos sintéticos
> porque la tabla real contiene información confidencial.

Evidencia: los generadores no contienen nombres, documentos ni importes reales.

## Diapositiva 4 — Cuatro capas

**Tiempo:** 90 segundos.

> El origen es ECC más SLT. AppFlow consume OData y deposita archivos en S3
> Landing. EC2 transforma particiones y conserva el resultado en Curated. RDS
> sirve el modelo dimensional a usuarios privados y Power BI mediante gateway.

Puntos para defender:

- Landing permite auditoría y reproceso.
- Curated separa validación de consumo.
- RDS no se expone públicamente.
- VPN es la primera fase; Direct Connect es una evolución.
- AppFlow productivo se activa cuando exista el `EntitySet` CO-PA validado.

## Diapositiva 5 — Capacidad base

**Tiempo:** 75 segundos.

> El universo de referencia es 45 millones de registros. Los 2 GiB observados
> en Datasphere están comprimidos y no se extrapolan directamente. Por eso
> estimamos rangos y exigimos una prueba sintética de al menos 4,5 millones de
> filas antes de producción.

Defender los números:

- carga inicial CSV estimada: 45–54 GiB;
- ETL: `m6i.large`, entre uno y cuatro workers;
- RDS: `db.m6g.large` Multi-AZ, 100 GiB ampliables a 200 GiB;
- incremento horario y crecimiento anual supuesto del 20 %;
- backups por 14 días y cifrado con KMS.

## Diapositiva 6 — Plan de migración

**Tiempo:** 75 segundos.

> El plan dura diez semanas. Primero resolvemos accesos, conectividad y
> Terraform. Después probamos función, volumen y recuperación. Finalmente
> ensayamos el corte, procesamos el delta final y habilitamos primero a un grupo
> piloto.

El corte se cancela si:

- hay una diferencia no explicada superior a 0,1 %;
- el delta permanece detenido durante más de dos horas;
- falla una consulta crítica;
- aparece un incidente grave de seguridad.

La reversa reactiva el consumo anterior y conserva Landing y RDS para diagnóstico.

## Diapositiva 7 — Costo

**Tiempo:** 75 segundos.

> El escenario productivo On-Demand cuesta aproximadamente USD 737 por mes. AWS
> Pricing Calculator informa USD 700,04 y la VPN, ausente del catálogo público,
> agrega USD 36,50 según la tarifa oficial. El 78,8 % está en RDS Multi-AZ y los
> dos nodos Windows del Power BI Gateway. S3 y
> AppFlow no dominan el presupuesto.

Explicar las alternativas:

- gateway corporativo existente: costo AWS aproximado de USD 454,06;
- ETL programado: ahorro frente a mantener el worker encendido permanentemente;
- reserva RDS: evaluar sólo después de medir carga real;
- lifecycle S3: archivar Landing y versiones antiguas.

El costo excluye impuestos, soporte, licencias, Direct Connect y mano de obra.

## Diapositiva 8 — Evidencia

**Tiempo:** 60 segundos más la demo.

> La entrega materializa cinco servicios AWS en LocalStack, ejecuta trece
> controles sin advertencias, aprueba cinco pruebas y valida Terraform 1.5.7. El
> próximo paso real no es copiar datos productivos: es confirmar el EntitySet
> OData de CO-PA con el equipo SAP.

Ejecutar:

```bash
./scripts/presentation_demo.sh
```

Durante la salida señalar:

1. creación o reutilización idempotente de los cinco servicios;
2. carga inicial de 1.000 registros y delta de 50;
3. consultas agregadas por sociedad y período;
4. resultado `13 OK / 0 WARN`;
5. costo mensual calculado desde el JSON versionado.

## Preguntas técnicas probables

### ¿Por qué AppFlow y no Airbyte o un integrador propio?

AppFlow dispone de conector SAP OData y admite carga completa seguida de
incrementales para proveedores ODP. Reduce código y operación del conector. La
decisión depende de validar el servicio OData real; si no cumple, se reevalúa el
patrón de ingesta.

### ¿SAP SLT expone directamente OData?

SLT actúa como proveedor ODP y administra la replicación/delta. La exposición
OData requiere SAP Gateway y configuración del servicio correspondiente. Por
eso el `EntitySet` figura como dependencia previa al piloto.

### ¿Cómo verificarían CE1xxxx antes de producción?

Se revisa la tabla en SLT, se confirma el proveedor ODP y su delta queue, se
publica/activa el servicio en SAP Gateway y se consulta el catálogo OData. Luego
se prueba lectura paginada y delta con un usuario técnico de sólo lectura.

### ¿Por qué RDS PostgreSQL y no Redshift?

El volumen inicial y el patrón dimensional son manejables con PostgreSQL, con
menor costo y complejidad. Si concurrencia, volumen o consultas superan los
umbrales definidos, Redshift o Athena se reevalúan como evolución.

### ¿Por qué no conectar Power BI directamente a RDS?

RDS permanece privado. Power BI Service usa un gateway con conexión TLS; los
usuarios corporativos entran por la red privada. No se publica el puerto 5432 a
Internet.

### ¿La VPN también se usa para los usuarios?

Sí para usuarios corporativos que consulten desde la red interna. El servicio
SaaS no usa automáticamente esa VPN: accede mediante el gateway autorizado.

### ¿Qué ocurre si se ejecuta la demo dos veces?

Los objetos sin cambios no se duplican y PostgreSQL utiliza upserts sobre la
clave de negocio. El resultado continúa siendo 1.050 registros únicos.

### ¿LocalStack demuestra seguridad real?

No completamente. Demuestra APIs, configuración y reproducibilidad. La
aplicación efectiva de políticas, KMS, Multi-AZ, VPN y rendimiento se valida en
una cuenta AWS de prueba antes de producción.

### ¿Los USD 736,54 son una cotización?

No. Son una estimación On-Demand reproducible con precios y cantidades
versionados. Fue recreada en AWS Pricing Calculator y debe revisarse nuevamente al aprobar el proyecto y
revisarse después de la prueba de volumen.

### ¿Qué dato falta confirmar?

El nombre y comportamiento del `EntitySet` OData que exponga CE1xxxx, incluida
la compatibilidad de delta. Esa es la dependencia técnica principal para pasar
de la simulación al piloto productivo.

## Cierre sugerido

> El proyecto deja una ruta controlada desde SAP ECC hasta el consumo analítico,
> sin usar datos confidenciales y sin exponer la base. La arquitectura está
> dimensionada, tiene cronograma, costos, reversa y evidencia reproducible. El
> siguiente hito es validar OData/ODP con SAP y ejecutar la prueba de volumen.
