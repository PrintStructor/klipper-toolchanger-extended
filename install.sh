#!/usr/bin/env bash
# klipper-toolchanger-extended install script (v2)

set -euo pipefail
export LC_ALL=C

# --- Paths ---------------------------------------------------------

# Wo Klipper installiert ist
KLIPPER_PATH="${KLIPPER_PATH:-${HOME}/klipper}"

# Pfad dieses Repos (Verzeichnis, in dem dieses Script liegt)
INSTALL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Klipper Config-Verzeichnis (Mainsail/Fluidd)
CONFIG_DIR="${CONFIG_DIR:-${HOME}/printer_data/config}"

# Moonraker-Konfiguration
MOONRAKER_CONF="${MOONRAKER_CONF:-${CONFIG_DIR}/moonraker.conf}"

# Beispiel-Configs im Repo
EXAMPLES_DIR="${INSTALL_PATH}/examples/atom-tc-6tool"

# Zielordner für Beispiel-Configs in Mainsail
EXAMPLES_TARGET_BASE="${CONFIG_DIR}/ATOM-toolchanger-examples"
EXAMPLES_TARGET_ATOM="${EXAMPLES_TARGET_BASE}/atom"

# --- Helper --------------------------------------------------------

info()  { echo "[INFO] $*"; }
warn()  { echo "[WARN] $*"; }
error() { echo "[ERROR] $*"; }

# --- Header --------------------------------------------------------

echo
echo "==========================================="
echo "- klipper-toolchanger-extended installer  -"
echo "==========================================="
echo

# --- Pre-Checks ----------------------------------------------------

if [[ "$EUID" -eq 0 ]]; then
  error "Do not run this script as root. Use your normal user (e.g. 'pi')."
  exit 1
fi

if [[ ! -d "${KLIPPER_PATH}/klippy/extras" ]]; then
  error "Klipper extras directory not found at: ${KLIPPER_PATH}/klippy/extras"
  error "Set KLIPPER_PATH or install Klipper first."
  exit 1
fi

# --- Link Python modules into Klipper -------------------------------

echo
info "Linking klipper-toolchanger-extended extras into Klipper ..."

EXTRAS_SRC="${INSTALL_PATH}/klipper/extras"
EXTRAS_DST="${KLIPPER_PATH}/klippy/extras"

if [[ ! -d "${EXTRAS_SRC}" ]]; then
  error "Extras directory not found: ${EXTRAS_SRC}"
  exit 1
fi

for f in "${EXTRAS_SRC}"/*.py; do
  bn="$(basename "$f")"
  info "  -> ${bn}"
  ln -sfn "$f" "${EXTRAS_DST}/${bn}"
done

echo
info "Restarting Klipper service ..."
sudo systemctl restart klipper || {
  error "Failed to restart Klipper via systemd."
  exit 1
}

# --- Moonraker update_manager block --------------------------------

echo
info "Configuring Moonraker update manager (optional) ..."

if [[ -f "${MOONRAKER_CONF}" ]]; then
  if grep -q "^\[update_manager klipper-toolchanger-extended\]" "${MOONRAKER_CONF}"; then
    info "Moonraker update_manager entry already present. Skipping."
  else
    cat <<EOF >> "${MOONRAKER_CONF}"

# klipper-toolchanger-extended update manager
[update_manager klipper-toolchanger-extended]
type: git_repo
path: ${INSTALL_PATH}
origin: https://github.com/PrintStructor/klipper-toolchanger-extended.git
primary_branch: main
managed_services: klipper
EOF
    echo
    info "Added [update_manager klipper-toolchanger-extended] to ${MOONRAKER_CONF}"
    info "Restarting Moonraker ..."
    sudo systemctl restart moonraker || warn "Could not restart Moonraker automatically."
  fi
else
  warn "Moonraker config not found at ${MOONRAKER_CONF}. Skipping update_manager setup."
fi

# --- Optional: Beispiel-Configs in Mainsail sichtbar machen --------

echo
info "Example configuration files"

if [[ ! -d "${CONFIG_DIR}" ]]; then
  warn "Klipper config directory not found at ${CONFIG_DIR}."
  warn "Skipping example config copy. You can copy them manually from:"
  echo "       ${EXAMPLES_DIR}"
else
  if [[ ! -d "${EXAMPLES_DIR}" ]]; then
    warn "Example directory not found: ${EXAMPLES_DIR}"
    warn "Skipping example config copy."
  else
    echo
    read -r -p "[CONFIG] Copy ATOM example configs into ${EXAMPLES_TARGET_BASE}? [y/N] " REPLY
    case "${REPLY}" in
      [yY][eE][sS]|[yY])
        echo
        info "Copying example configs ..."

        mkdir -p "${EXAMPLES_TARGET_ATOM}"

        # printer.cfg -> printer_example.cfg (kein Drop-in!)
        if [[ -f "${EXAMPLES_DIR}/printer.cfg" ]]; then
          if [[ -f "${EXAMPLES_TARGET_BASE}/printer_example.cfg" ]]; then
            warn "printer_example.cfg already exists in target. Leaving as is."
          else
            cp "${EXAMPLES_DIR}/printer.cfg" "${EXAMPLES_TARGET_BASE}/printer_example.cfg"
            info "  -> printer_example.cfg"
          fi
        fi

        # alle anderen .cfg im Beispiel-Hauptverzeichnis (ohne printer.cfg)
        for cfg in "${EXAMPLES_DIR}"/*.cfg; do
          bn="$(basename "$cfg")"
          [[ "${bn}" == "printer.cfg" ]] && continue
          if [[ -f "${EXAMPLES_TARGET_BASE}/${bn}" ]]; then
            warn "  -> ${bn} already exists in target. Skipping."
          else
            cp "${cfg}" "${EXAMPLES_TARGET_BASE}/${bn}"
            info "  -> ${bn}"
          fi
        done

        # atom/*.cfg
        if [[ -d "${EXAMPLES_DIR}/atom" ]]; then
          for cfg in "${EXAMPLES_DIR}/atom"/*.cfg; do
            bn="$(basename "$cfg")"
            if [[ -f "${EXAMPLES_TARGET_ATOM}/${bn}" ]]; then
              warn "  -> atom/${bn} already exists in target. Skipping."
            else
              cp "${cfg}" "${EXAMPLES_TARGET_ATOM}/${bn}"
              info "  -> atom/${bn}"
            fi
          done
        fi

        echo
        info "Example configs copied to:"
        echo "  ${EXAMPLES_TARGET_BASE}"
        echo
        echo "You can now open them in Mainsail/Fluidd under:"
        echo "  Machine -> Config Files -> ATOM-toolchanger-examples/"
        echo
        echo "Typical includes you will add to your real printer.cfg"
        echo "(after moving/adjusting the configs to your preferred layout):"
        echo
        echo "  [include atom/toolchanger.cfg]"
        echo "  [include atom/toolchanger_macros.cfg]"
        echo "  [include atom/beacon.cfg]"
        echo "  [include atom/T0.cfg]"
        echo "  [include atom/T1.cfg]"
        echo "  [include atom/T2.cfg]"
        echo "  [include atom/T3.cfg]"
        echo "  [include atom/T4.cfg]"
        echo "  [include atom/T5.cfg]"
        echo
        echo "IMPORTANT:"
        echo "  These example configs are based on my own machine."
        echo "  You MUST adjust:"
        echo "   - CAN UUIDs"
        echo "   - dock positions and coordinates"
        echo "   - probe offsets & speeds"
        echo "   - homing positions & limits"
        echo "  before attempting any toolchanger moves."
        ;;
      *)
        info "Skipping example config copy."
        ;;
    esac
  fi
fi

echo
info "Installation finished."
echo "klipper-toolchanger-extended is linked to Klipper."
echo