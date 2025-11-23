#!/usr/bin/env bash
# klipper-toolchanger-extended install script (v2.2)

set -euo pipefail
export LC_ALL=C

###############################################################################
# Paths & defaults
###############################################################################

# Where Klipper is installed
KLIPPER_PATH="${KLIPPER_PATH:-${HOME}/klipper}"

# Path to this repository (directory of this script)
INSTALL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Klipper config directory (Mainsail/Fluidd)
CONFIG_DIR="${CONFIG_DIR:-${HOME}/printer_data/config}"

# Moonraker config
MOONRAKER_CONF="${MOONRAKER_CONF:-${CONFIG_DIR}/moonraker.conf}"

# Example configs in this repo
EXAMPLES_DIR="${EXAMPLES_DIR:-${INSTALL_PATH}/examples/atom-tc-6tool}"

# Target dirs for example configs (visible in Mainsail)
EXAMPLES_TARGET_BASE="${CONFIG_DIR}/ATOM-toolchanger-examples"
EXAMPLES_TARGET_ATOM="${EXAMPLES_TARGET_BASE}/atom"

###############################################################################
# Helper functions
###############################################################################

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*"; }
error() { echo "[ERROR] $*"; }

###############################################################################
# Header
###############################################################################

echo
echo "==========================================="
echo "- klipper-toolchanger-extended installer  -"
echo "==========================================="
echo

###############################################################################
# Pre-checks
###############################################################################

if [[ "$EUID" -eq 0 ]]; then
  error "Do not run this script as root. Use your normal user (e.g. 'pi')."
  exit 1
fi

if [[ ! -d "${KLIPPER_PATH}/klippy/extras" ]]; then
  error "Klipper extras directory not found at:"
  echo "       ${KLIPPER_PATH}/klippy/extras"
  error "Set KLIPPER_PATH or install Klipper first."
  exit 1
fi

###############################################################################
# Link Python modules into Klipper
###############################################################################

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
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart klipper || {
    error "Failed to restart Klipper via systemd."
    exit 1
  }
else
  warn "systemctl not found; please restart Klipper manually."
fi

###############################################################################
# Configure Moonraker update_manager
###############################################################################

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

    if command -v systemctl >/dev/null 2>&1; then
      info "Restarting Moonraker ..."
      sudo systemctl restart moonraker || warn "Could not restart Moonraker automatically."
    else
      warn "systemctl not found; please restart Moonraker manually."
    fi
  fi
else
  warn "Moonraker config not found at ${MOONRAKER_CONF}. Skipping update_manager setup."
fi

###############################################################################
# Optional: copy example configs into Mainsail config dir
###############################################################################

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

        # If examples target already exists, offer to reset it
        if [[ -d "${EXAMPLES_TARGET_BASE}" ]]; then
          warn "Existing example directory detected at:"
          echo "       ${EXAMPLES_TARGET_BASE}"
          read -r -p "[CONFIG] Remove and recreate this directory? (will delete old example files) [y/N] " CLEAN_REPLY
          case "${CLEAN_REPLY}" in
            [yY][eE][sS]|[yY])
              info "Removing old example directory ..."
              rm -rf "${EXAMPLES_TARGET_BASE}"
              ;;
            *)
              info "Keeping existing example directory; new files will be added on top."
              ;;
          esac
        fi

        info "Copying example configs ..."
        mkdir -p "${EXAMPLES_TARGET_ATOM}"

        # 1) Sort all *.cfg in EXAMPLES_DIR into appropriate targets
        for cfg in "${EXAMPLES_DIR}"/*.cfg; do
          [[ -e "$cfg" ]] || continue
          bn="$(basename "$cfg")"
          dest=""

          case "${bn}" in
            # printer.cfg -> printer_example.cfg (not a drop-in!)
            printer.cfg)
              dest="${EXAMPLES_TARGET_BASE}/printer_example.cfg"
              ;;

            # Files that belong to the ATOM/toolchanger block
            T*.cfg|calibrate_offsets.cfg|toolchanger.cfg|toolchanger_macros.cfg|knomi.cfg|tc_led_effects.cfg|beacon.cfg)
              dest="${EXAMPLES_TARGET_ATOM}/${bn}"
              ;;

            # Other files (macros.cfg, mainsail.cfg, shell_command.cfg, etc.)
            *)
              dest="${EXAMPLES_TARGET_BASE}/${bn}"
              ;;
          esac

          if [[ -z "${dest}" ]]; then
            continue
          fi

          if [[ -f "${dest}" ]]; then
            warn "  -> $(basename "${dest}") already exists. Skipping."
          else
            cp "${cfg}" "${dest}"
            rel="${dest#${CONFIG_DIR}/}"
            info "  -> ${rel}"
          fi
        done

        # 2) If there is already an atom/ subdirectory in the repo, copy those as well
        if [[ -d "${EXAMPLES_DIR}/atom" ]]; then
          for cfg in "${EXAMPLES_DIR}/atom"/*.cfg; do
            [[ -e "$cfg" ]] || continue
            bn="$(basename "$cfg")"
            dest="${EXAMPLES_TARGET_ATOM}/${bn}"

            if [[ -f "${dest}" ]]; then
              warn "  -> atom/${bn} already exists. Skipping."
            else
              cp "${cfg}" "${dest}"
              rel="${dest#${CONFIG_DIR}/}"
              info "  -> ${rel}"
            fi
          done
        fi

        echo
        info "Example configs are available at:"
        echo "  ${EXAMPLES_TARGET_BASE}"
        echo
        echo "You can now open them in Mainsail/Fluidd under:"
        echo "  Machine -> Config Files -> ATOM-toolchanger-examples/"
        echo
        echo "Typical includes you will add to your REAL printer.cfg"
        echo "(after moving/renaming the configs to your preferred layout):"
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
        echo "  You MUST adjust at least:"
        echo "    - CAN UUIDs for toolhead boards"
        echo "    - Dock positions & coordinates"
        echo "    - Probe offsets & speeds"
        echo "    - Homing positions & limits"
        echo "  before attempting any toolchanger moves."
        ;;

      *)
        info "Skipping example config copy."
        ;;
    esac
  fi
fi

###############################################################################
# Done
###############################################################################

echo
info "Installation finished."
echo "klipper-toolchanger-extended is now linked to Klipper."
echo