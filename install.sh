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

printf "\n======================================\n"
echo "- Klipper toolchanger-extended install script -"
printf "======================================\n\n"

# Run steps
preflight_checks
check_download
link_extension
restart_klipper

echo "[DONE] Installation finished."
