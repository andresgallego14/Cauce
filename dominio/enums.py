from enum import StrEnum


class TipoMovimiento(StrEnum):
    ENTRADA = "entrada"
    SALIDA = "salida"

class Fuente(StrEnum):
    FERTIRRIEGO = "fertirriego"
    LLUVIA = "lluvia"
    RIEGO = "riego"
    CRUDA = "cruda"
    AGUA_POTABLE_60 = "agua_potable_60"
    AGUA_POTABLE_370 = "agua_potable_370"

    @property
    def tipo(self) -> TipoMovimiento:
        if self in (Fuente.FERTIRRIEGO, Fuente.LLUVIA):
            return TipoMovimiento.ENTRADA
        return TipoMovimiento.SALIDA
    
class Bocatoma(StrEnum):
    BOCATOMA_1 = "Bocatoma 1"
    BOCATOMA_2 = "Bocatoma 2"
    SUMERGIBLE = "Bocatoma Sumergible" 
