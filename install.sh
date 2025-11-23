#!/bin/bash

# Repo and paths
REPO="PrintStructor/klipper-toolchanger-extended.git"
KLIPPER_PATH="${HOME}/klipper"
INSTALL_PATH="${HOME}/klipper-toolchanger-extended"

set -eu
export LC_ALL=C

function preflight_checks {
  if [ "$EUID" -eq 0 ]; then
    echo "[PRE-CHECK] This script must not be run as root!"
    exit -1
  fi

  if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F 'klipper.service')" ]; then
    printf "[PRE-CHECK] Klipper service found! Continuing...\n\n"
  else
    echo "[ERROR] Klipper service not found, please install Klipper first!"
    exit -1
  fi
}

function check_download {
  local installdirname
  local installbasename

  installdirname="$(dirname ${INSTALL_PATH})"
  installbasename="$(basename ${INSTALL_PATH})"

  if [ ! -d "${INSTALL_PATH}" ]; then
    echo "[DOWNLOAD] Cloning repository..."
    if git -C "${installdirname}" clone "https://github.com/${REPO}" "${installbasename}"; then
      chmod +x "${INSTALL_PATH}/install.sh"
      printf "[DOWNLOAD] Download complete!\n\n"
    else
      echo "[ERROR] Download of git repository failed!"
      exit -1
    fi
  else
    printf "[DOWNLOAD] Repository already found locally at %s. Continuing...\n\n" "${INSTALL_PATH}"
  fi
}

function link_extension {
  echo "[INSTALL] Linking extension to Klipper..."
  for file in "${INSTALL_PATH}"/klipper/extras/*.py; do
    ln -sfn "${file}" "${KLIPPER_PATH}/klippy/extras/"
  done
}

function restart_klipper {
  echo "[POST-INSTALL] Restarting Klipper..."
  sudo systemctl restart klipper
}

function setup_moonraker_updater {
  local moonraker_conf="${HOME}/printer_data/config/moonraker.conf"
  
  echo ""
  echo "=========================================="
  echo "Moonraker Update Manager Setup (Optional)"
  echo "=========================================="
  echo ""
  echo "Would you like to add this extension to Moonraker's update manager?"
  echo "This allows automatic updates via Mainsail/Fluidd web interface."
  echo ""
  read -p "Setup Moonraker updater? (y/N): " -n 1 -r
  echo ""
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "${moonraker_conf}" ]; then
      # Check if already configured
      if grep -q "\[update_manager klipper-toolchanger-extended\]" "${moonraker_conf}"; then
        echo "[MOONRAKER] Already configured in moonraker.conf, skipping..."
      else
        echo "[MOONRAKER] Adding update manager configuration..."
        cat >> "${moonraker_conf}" << 'EOF'

# ==============================================================================
# Klipper Toolchanger Extended - Auto Update Configuration
# ==============================================================================

[update_manager klipper-toolchanger-extended]
type: git_repo
path: ~/klipper-toolchanger-extended
origin: https://github.com/PrintStructor/klipper-toolchanger-extended.git
primary_branch: main
managed_services: klipper
install_script: install.sh
EOF
        echo "[MOONRAKER] Configuration added successfully!"
        echo "[MOONRAKER] Restarting Moonraker..."
        sudo systemctl restart moonraker
        echo "[MOONRAKER] Done! Check for updates in Mainsail/Fluidd interface."
      fi
    else
      echo "[MOONRAKER] Warning: moonraker.conf not found at ${moonraker_conf}"
      echo "[MOONRAKER] You can manually add the configuration later."
      echo "[MOONRAKER] See moonraker.conf in this repository for details."
    fi
  else
    echo "[MOONRAKER] Skipped. You can add it manually later if needed."
    echo "[MOONRAKER] See moonraker.conf in this repository for configuration."
  fi
}

printf "\n======================================\n"
echo "- Klipper toolchanger-extended install script -"
printf "======================================\n\n"

# Run steps
preflight_checks
check_download
link_extension
restart_klipper
setup_moonraker_updater

echo ""
echo "[DONE] Installation finished successfully!"
echo ""
echo "Next steps:"
echo "  1. Add configuration to your printer.cfg"
echo "  2. See examples/atom-tc-6tool/ for reference configuration"
echo "  3. Customize for your specific hardware setup"
echo "  4. Restart Klipper: sudo systemctl restart klipper"
echo ""
