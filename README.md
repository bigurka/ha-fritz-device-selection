# FRITZ!Box Tools – device selection

🇮🇹 [Italiano](#italiano) · 🇬🇧 [English](#english)

---

## Italiano

Versione modificata dell'integrazione ufficiale **FRITZ!Box Tools** (`fritz`) di Home Assistant
che permette di **scegliere quali dispositivi della rete integrare**.

L'integrazione ufficiale crea un dispositivo, un tracker di presenza, un interruttore
"accesso a Internet" e un pulsante Wake on LAN per **ogni** apparecchio conosciuto dal
FRITZ!Box: con decine di telefoni, TV, prese e lampadine la lista diventa ingestibile.

### Cosa cambia rispetto all'originale

- **Dispositivi di rete da integrare**: nelle opzioni (Impostazioni → Dispositivi e servizi →
  FRITZ!Box Tools → Configura) compare l'elenco di tutti i dispositivi conosciuti dal FRITZ!Box,
  con nome, IP e MAC. Solo quelli spuntati vengono integrati.
- **Togli tutte le spunte / Spunta tutti i dispositivi**: spunta una delle due caselle sopra l'elenco e
  premi Invia: l'elenco si riapre tutto vuoto o tutto spuntato senza salvare niente, poi sistemi le
  spunte e premi di nuovo Invia. Se le spunti entrambe vince "Togli tutte le spunte".
- **Rimozione automatica**: i dispositivi tolti dalla selezione vengono rimossi da Home Assistant
  insieme alle loro entità al primo aggiornamento (entro 30 secondi). È il modo per fare pulizia
  di massa in un'installazione esistente.
- **Aggiungi automaticamente i nuovi dispositivi**: se attivo (predefinito, come l'originale) i
  dispositivi che compaiono in futuro vengono aggiunti da soli; se disattivo vengono integrati
  solo quelli selezionati.
- **Elimina dal singolo dispositivo**: nella pagina di un dispositivo di rete compare il comando
  "Elimina"; il dispositivo viene rimosso e non viene più aggiunto.
- Sui ripetitori in mesh (che non tracciano dispositivi) l'elenco non viene mostrato.

Tutto il resto (sensori, interruttori Wi-Fi, chiamate, aggiornamento firmware…) è identico
all'integrazione ufficiale della versione indicata in `manifest.json`.

### Installazione

> ⚠️ Questa integrazione **sostituisce** quella ufficiale `fritz` (stesso nome): Home Assistant
> mostra un avviso per le integrazioni personalizzate. Le configurazioni esistenti restano valide.
> Fai un backup prima di installarla.

**HACS**: HACS → menu ⋮ → Repository personalizzati → aggiungi
`https://github.com/bigurka/ha-fritz-device-selection` come *Integrazione*, installa e riavvia
Home Assistant.

**Manuale**: copia la cartella `custom_components/fritz` in `config/custom_components/` e riavvia.

**Disinstallazione**: elimina `config/custom_components/fritz` e riavvia: torna in uso
l'integrazione ufficiale. I dispositivi esclusi vengono ricreati da quella ufficiale.

### Compatibilità

Basata sul codice di Home Assistant **2026.11.0**. Dopo un aggiornamento di Home Assistant
controlla che sia disponibile una versione allineata di questa integrazione.

---

## English

Modified version of the official Home Assistant **FRITZ!Box Tools** integration (`fritz`) that
lets you **choose which network devices are integrated**.

The official integration creates a device, a presence tracker, an "internet access" switch and a
Wake on LAN button for **every** host known by the FRITZ!Box: with dozens of phones, TVs, plugs
and bulbs the list becomes unmanageable.

### Changes compared to the original

- **Network devices to integrate**: the options (Settings → Devices & services →
  FRITZ!Box Tools → Configure) list all devices known by the FRITZ!Box, with name, IP and MAC.
  Only the checked ones are integrated.
- **Untick all devices / Tick all devices**: tick one of the two boxes above the list and press
  Submit: the list opens again all unticked or all ticked and nothing is saved, then adjust it and
  press Submit again. If both are ticked, "Untick all devices" wins.
- **Automatic removal**: deselected devices are removed from Home Assistant together with their
  entities on the next update (within 30 seconds). This is how to clean up an existing
  installation in bulk.
- **Add new devices automatically**: when enabled (default, same as the original) devices that
  show up later are added automatically; when disabled only the selected ones are integrated.
- **Delete a single device**: the page of a network device offers "Delete"; the device is removed
  and not added again.
- On mesh repeaters (which do not track devices) the list is not shown.

Everything else (sensors, Wi-Fi switches, calls, firmware update…) is identical to the official
integration of the version stated in `manifest.json`.

### Installation

> ⚠️ This integration **replaces** the official `fritz` integration (same domain): Home Assistant
> shows a warning for custom integrations. Existing config entries keep working. Make a backup
> before installing it.

**HACS**: HACS → ⋮ menu → Custom repositories → add
`https://github.com/bigurka/ha-fritz-device-selection` as *Integration*, install and restart
Home Assistant.

**Manual**: copy the `custom_components/fritz` folder into `config/custom_components/` and restart.

**Uninstall**: delete `config/custom_components/fritz` and restart: the official integration is
used again. Excluded devices are created again by the official integration.

### Compatibility

Based on the Home Assistant **2026.11.0** code. After a Home Assistant update check that an
aligned version of this integration is available.

---

## Credits and license / Crediti e licenza

Derived from the official `fritz` integration of
[Home Assistant Core](https://github.com/home-assistant/core/tree/2026.11.0/homeassistant/components/fritz)
by its authors (codeowners: @AaronDavidSchneider, @chemelli74, @mib1185) and the Home Assistant
contributors, released under the [Apache License 2.0](LICENSE).
Modified by @bigurka: device selection options, removal of deselected devices, device deletion.
Modified files: `__init__.py`, `config_flow.py`, `const.py`, `coordinator.py`, `manifest.json`,
`strings.json`, `translations/en.json`, `translations/it.json`.

Not affiliated with or endorsed by AVM or the Home Assistant project. FRITZ! is a trademark of AVM GmbH.
Non affiliato né approvato da AVM o dal progetto Home Assistant. FRITZ! è un marchio di AVM GmbH.
