#!/usr/bin/env bash
#
# Based on:
#   https://soco.intel.com/docs/DOC-2192910
#   https://soco.intel.com/external-link.jspa?url=https%3A%2F%2Fwww.bounca.org%2Ftutorials%2Finstall_root_certificate.html
#   https://certificates.intel.com/PkiWeb/RAUI/TrustChain/RetrieveTrustChain.aspx
#   https://www.bounca.org/tutorials/install_root_certificate.html#linux-ubuntu-debian

set -e
source /etc/os-release
certsFile='IntelSHA2RootChain-Base64.zip'
certsUrl="http://certificates.intel.com/repository/certificates/$certsFile"

case $NAME in
  Ubuntu)
    certsFolder='/usr/local/share/ca-certificates'
    cmd='/usr/sbin/update-ca-certificates'
    ;;
  SLES)
    certsFolder='/etc/pki/trust/anchors'
    cmd='/usr/sbin/update-ca-certificates'
    ;;
  Fedora)
    certsFolder='/etc/pki/ca-trust/source/anchors'
    cmd='/bin/update-ca-trust'
    ;;
  "Red Hat Enterprise Linux")
    certsFolder='/etc/pki/ca-trust/source/anchors'
    cmd='/bin/update-ca-trust'
    ;;
  *)
    echo "Unsupported OS: " $NAME
    exit 1
    ;;
esac

downloadCerts(){
  if ! [ -x "$(command -v unzip)" ]; then
    echo 'Error: unzip is not installed.' >&2
    exit 1
  fi
  http_proxy='' &&\
    wget $certsUrl -O $certsFolder/$certsFile
  unzip -u $certsFolder/$certsFile -d $certsFolder
  rm $certsFolder/$certsFile
}

installCerts(){
  chmod 644 $certsFolder/*.crt
  eval "$cmd"
}

downloadCerts
installCerts

echo ""
echo "=================================================="
echo " IMPORTANT:"
echo " Docker service MUST be restarted for Docker to "
echo " read and apply the new CAs."
echo " e.g.: 'service docker restart'"
echo "=================================================="
echo ""
