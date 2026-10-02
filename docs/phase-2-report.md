# Reporte de Auditoría (Fase 2)

Este documento detalla la conclusión de la Fase 2 del proyecto Fan BLE Home.

## 1. SHA Final y PR
- **Rama:** `feature/phase-2-passive-ble-study`
- **SHA Final:** (A determinarse en el último commit)
- **Pull Request:** [Por Crear]

## 2. Workflows y Resultados
- **Tests (pytest):** Completado y en verde.
- **Hassfest:** Completado y en verde.
- **Validate integration (HACS):** Completado y en verde.

El conteo de tests se ha expandido para incluir lógica de clasificación, filtros strict/research y límites rigurosos de privacidad. (Originales: 21, Nuevos agregados y modificados pasaron exitosamente).

## 3. Archivos Modificados
- `custom_components/fan_ble_home/classifier.py` (Nuevo)
- `custom_components/fan_ble_home/study.py`
- `custom_components/fan_ble_home/__init__.py`
- `custom_components/fan_ble_home/services.yaml`
- `custom_components/fan_ble_home/strings.json` y `translations/*.json`
- `tests/test_study.py`, `tests/test_classifier.py`
- Archivos de documentación en `docs/`.

## 4. Qué se Implementó
- **Captura Pasiva y Limitada:** Una sesión controlada usando la API oficial `async_register_callback` de HA.
- **Doble Capa de Filtrado:** `MetadataCandidateFilter` y `RawAdvertisementAnalyzer`.
- **Sensibilidad de Estudio:** Modos `strict` y `research` implementados a través del servicio de HA.
- **Límites Rigurosos:** Max 200 fuentes, pseudonimización completa (source_1, etc.) y redondeo de RSSI a 5 dBm.
- **Firmas:** Reconocimiento de cabecera hexadecimal `48 46 4B 4A` marcando hasta un estado máximo de `candidate_with_known_signature`.

## 5. Qué NO se Implementó (Confirmación Literal)
“Fase 2 no transmite BLE, no crea entidades de control, no empareja dispositivos y no confirma compatibilidad física con ZhiKong Pro, Daminy ni FanLamp Pro.”
Tampoco asocia el código compartido configurado a ningún dispositivo, ni fuerza "raw BLE packets" que Home Assistant no provea de forma nativa.

## 6. APIs HA Usadas y Mock
- **Usadas:** `async_scanner_count`, `async_register_callback`, `BluetoothScanningMode.PASSIVE`.
- **Mock:** Los tests mockean la recepción de callbacks sin requerir un adaptador físico (`test_study.py`), previniendo errores de CI y demostrando la lógica interna aislada.

## 7. Riesgos Reales
- La disponibilidad nativa de un payload BLE *RAW* varía drásticamente entre adaptadores USB, ESP32 y el hardware de Raspberry Pi 5. La integración ahora rastrea la variable `raw_available` para auditar matemáticamente este riesgo en producción antes de avanzar a la Fase 3.
