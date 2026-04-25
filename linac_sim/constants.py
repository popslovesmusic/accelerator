"""Physical constants in SI units."""

SPEED_OF_LIGHT = 299_792_458.0
ELEMENTARY_CHARGE = 1.602_176_634e-19
PROTON_MASS = 1.672_621_923_69e-27
ELECTRON_MASS = 9.109_383_7015e-31
EV_TO_JOULE = ELEMENTARY_CHARGE
JOULE_TO_EV = 1.0 / ELEMENTARY_CHARGE


PARTICLE_SPECIES = {
    "proton": {
        "mass_kg": PROTON_MASS,
        "charge_c": ELEMENTARY_CHARGE,
    },
    "electron": {
        "mass_kg": ELECTRON_MASS,
        "charge_c": -ELEMENTARY_CHARGE,
    },
}
