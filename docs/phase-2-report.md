# Reporte de Auditoría (Fase 2)

Este documento detalla la conclusión corregida de la Fase 2 del proyecto Fan BLE Home.

## 1. SHA Final y PR
- **Rama:** `feature/phase-2-passive-ble-study`
- **SHA Final:** (A determinarse en el último commit)
- **Pull Request:** [PR #2]

## 2. Workflows y Resultados
- **Tests (pytest):** Completado y en verde.
- **Hassfest:** Completado y en verde.
- **Validate integration (HACS):** Completado y en verde.

El conteo de tests se ha expandido para incluir pruebas rigurosas de aislamiento entre metadata y raw data.

## 3. APIs HA Usadas y Manejo Raw
- **Usadas:** `async_scanner_count`, `async_register_callback`, `BluetoothScanningMode.PASSIVE`.
- **Manejo Raw:** La integración *no sintetiza ni deriva* bytes raw a partir de `manufacturer_data`. El analizador `RawAdvertisementAnalyzer` evalúa exclusivamente los bytes crudos en bruto provistos de forma nativa. De lo contrario, `raw_available` se marca como `false` y `raw_available_count` permanece en 0. Se acepta legítimamente que un adaptador no provea tráfico raw nativo.

## 4. Qué se Implementó
- **Captura Pasiva y Limitada:** Una sesión controlada usando la API oficial `async_register_callback` de HA.
- **Separación Estricta:** `MetadataCandidateFilter` opera sobre metadata (`low` confidence, `unknown` status); `RawAdvertisementAnalyzer` opera sobre raw nativo validando AD type, longitud y header.
- **Sensibilidad de Estudio:** 
  - `strict`: Si no existe raw nativo, no hay candidatos y se conservan 0 muestras erróneas.
  - `research`: Agrega conteos y alias sin inventar clasificaciones ni incrementar `candidates_count`.
- **Límites Rigurosos:** Max 200 fuentes, pseudonimización completa (source_1, etc.) y redondeo de RSSI a 5 dBm.

## 5. Qué NO se Implementó (Confirmación Literal)
“Fase 2 no transmite BLE, no crea entidades de control, no empareja dispositivos y no confirma compatibilidad física con ZhiKong Pro, Daminy ni FanLamp Pro.”
Tampoco asocia el código compartido configurado a ningún dispositivo, ni fuerza "raw BLE packets" o identificadores falsos que Home Assistant no provea de forma nativa.

## 6. Riesgos Reales
- La disponibilidad nativa de un payload BLE *RAW* varía drásticamente entre adaptadores USB, ESP32 y el hardware de Raspberry Pi 5. De no proveerse, el modo `strict` arrojará 0 resultados válidos en producción. Esta es la consecuencia correcta y esperada antes de avanzar a la Fase 3, donde la obtención confiable de los payloads deberá tratarse.
