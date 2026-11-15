#!/bin/sh
# The one command that proves mom-character works. Exit 0 = pass, anything else = fail.
# Written or approved by Nick. Agents may run it, never edit it.
cd "$(dirname "$0")" && exec python3 -I checks/check_scripts.py
