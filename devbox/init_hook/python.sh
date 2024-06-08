# BEGIN DOTGIT-SYNC BLOCK MANAGED
#!/usr/bin/env bash
# """TODO
# """

# shellcheck disable=SC2034
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1 ; pwd -P )"
SCRIPTNAME="$(basename "$0")"
LOG_FILE="${SCRIPTPATH}/${SCRIPTNAME}.log"

init_logger(){
  local log_file="${XDG_CACHE_HOME:-${HOME}/.cache}/snippets/_log.sh"
  local last_download_file="/tmp/_log.time"
  local delai=14400             # 4 hours
  # shellcheck disable=SC2155
  local curr_time=$(date +%s)
  local time="$(( curr_time - $(cat "${last_download_file}" 2>/dev/null || echo "0") ))"

  if ! [[ -f "${log_file}" ]] \
    || { [[ -f "${log_file}" ]] && [[ "${time}" -gt "${delai}" ]]; }
  then
    if ping -q -c 1 -W 1 framagit.org &> /dev/null
    then
      # shellcheck disable=SC1090
      source <(curl -s https://framagit.org/-/snippets/7183/raw/main/_get_log.sh)
      echo "${curr_time}" > "${last_download_file}"
    else
      echo -e "\033[1;33m[WARNING]\033[0;33m Unable to get last logger version, will use \`echo\`.\033[0m"
      _log(){
        echo "$@"
      }
    fi
  else
    # shellcheck disable=SC1090
    source <(cat "${log_file}")
  fi
}

install_requirements(){
  local type="$1"
  local not_pinned="${PWD}/requirements.${type}.in"
  local pinned="${PWD}/requirements.${type}.txt"

  if ! [[ -f "${not_pinned}" ]] && ! [[ -f "${pinned}" ]]
  then
    _log "WARNING" "devbox: None of the following python requirements exists, nothing to do"
    _log "WARNING" "devbox:   * ${not_pinned}"
    _log "WARNING" "devbox:   * ${pinned}"
    return
  elif ! [[ -f "${pinned}" ]]
  then
    pip-compile "${not_pinned}" >> "${LOG_FILE}"
  fi

  _log "INFO" "devbox: Installing python requirements from ${pinned}"
  pip install -r "${pinned}" >> "${LOG_FILE}"
}

main(){
  # TODO Change below substitution if need
  local DEBUG_LEVEL="${DEVBOX_DEBUG_LEVEL:-INFO}"
  init_logger

  _log "INFO" "devbox: Installing python dependencies"
  pip3 install pip-tools >> "${LOG_FILE}"
  install_requirements "dev"
  install_requirements "prod"
  install_requirements "doc"
}

main "$@"

# vim: ft=sh

# END DOTGIT-SYNC BLOCK MANAGED
