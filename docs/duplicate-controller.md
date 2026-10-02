# Duplicate Controller Configuration

Fan BLE Home utilizes a **Duplicate Controller Configuration** flow to securely and reliably pair with your physical fan/light using a previously paired BLE remote (e.g., ZhiKong Pro).

## Propósito
El flujo de "Duplicar controlador existente" escucha temporalmente los comandos BLE Raw emitidos por un mando a distancia físico o una aplicación móvil. Una vez que se identifica y valida el comando (por ejemplo, encender la luz principal), Fan BLE Home extrae los parámetros mínimos necesarios para reproducir esa orden de manera local.

Solo cuando una prueba física confirmada (ej. un parpadeo de luz reversible) tiene éxito, la integración procede a crear las entidades correspondientes en Home Assistant (`fan` y `light`). Esto evita entidades falsas o "fantasma" que no funcionan.

## Limitaciones y Requisitos de Hardware
La duplicación **requiere** que el adaptador Bluetooth proporcione *Raw Advertising Data* (bytes crudos completos).
Lamentablemente, no todos los adaptadores Bluetooth ni todas las integraciones de Home Assistant exponen esta información.

- **Soportado (Generalmente):**
  - Adaptadores locales en Linux (ej. Raspberry Pi 5) mediante BlueZ (cuando la API de HA transfiere los detalles correctamente).
  - Nodos ESPHome configurados con `ble_adv_proxy` (si entregan la estructura raw esperada).

- **No Soportado:**
  - Adaptadores que solo exponen *Metadata* (Service UUIDs, Manufacturer Data parcial) sin proveer la estructura completa del paquete. En este escenario, el flujo se detendrá con un mensaje de error claro y no permitirá la configuración, ya que la reconstrucción de paquetes sin raw data es propensa a fallos.

## Flujo de Configuración
1. **Verificación de Transporte:** Fan BLE Home verifica que exista un adaptador que provea Raw BLE.
2. **Detección de Candidato:** Presiona cualquier botón en el mando a distancia para que la integración identifique el protocolo (ej. ZhiKong Pro).
3. **Acciones Guiadas:** Sigue las instrucciones en pantalla para presionar botones específicos (Light On, Fan On, Fan Speed, etc.) durante ventanas de 10 a 20 segundos.
4. **Validación (Blink Test):** La integración enviará una orden de prueba. Si confirmas físicamente que el ventilador/luz respondió, se crearán las entidades.

## Ecosistema (Matter/HAP)
Fan BLE Home no expone *directamente* el ventilador hacia Apple HomeKit ni Matter. Se encarga única y exclusivamente de crear las entidades locales (`fan`, `light`) en Home Assistant. Se recomienda el uso de un add-on como "Matter All-in-One" o la integración nativa de HomeKit Bridge en Home Assistant para exportar estas entidades a tus controladores inteligentes externos.
