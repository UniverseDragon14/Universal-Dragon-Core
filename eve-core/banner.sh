#!/usr/bin/env bash
# EVE / Universal Dragon banners. Sourced by eve-core modules.

eve_banner() {
  printf '%s' "$C_MAG" >&2
  cat >&2 <<'ART'
        ______     _______
       / ____/  ___/ / ____/
      / __/  \/ _ \ / __/       U N I V E R S A L   D R A G O N
     / /___ /  __/  /___
    /_____/  \___/_____/         E · V · E   ·   N O V A   C O R E
ART
  printf '%s' "$C_RESET" >&2
  printf '%s    Forged by Aslam · Quantum-Level QBIT NOVA Engine · v%s%s\n\n' \
    "$C_DIM" "$EVE_VERSION" "$C_RESET" >&2
}

eve_dragon() {
  printf '%s' "$C_CYAN" >&2
  cat >&2 <<'ART'
               /\                 /\
              / \'._   (\_/)   _.'/ \
             /_.''._'--('.')--'_.''._\
             | \_ / `;=/ " \=;` \ _/ |
              \/ `\__|`\___/`|__/`  \/
                    \(/|\)/
                     " ` "
ART
  printf '%s\n' "$C_RESET" >&2
}
