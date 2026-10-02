# Third-Party Notices

This project uses and adapts concepts, architecture structures, and testing fixtures from third-party open-source projects. We express our gratitude to the authors of these projects.

## ha-ble-adv
- **Source:** https://github.com/NicoIIT/ha-ble-adv
- **License:** MIT License
- **Author/Copyright:** Copyright (c) 2024 NicoIIT
- **Adaptation Details:**
  Fan BLE Home uses protocol concepts, decoding algorithms, and payload structures from `ha-ble-adv` as a technical reference to build the "ZhiKong Pro" (ZhiMei) protocol profile. We have adapted the matrix transformations, checksum algorithms, and certain testing fixtures from `ha-ble-adv` for decoding and encoding physical BLE raw packets, strictly limiting our implementation to the ZhiKong Pro profile under the Fan BLE Home architecture.

### MIT License (ha-ble-adv)
```
MIT License

Copyright (c) 2024 NicoIIT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
