from app_resources import AppCache


## INST ##

# Verrà istanziata la prima (e unica) volta che questo file viene importato.
# L'istanza è immediatamente disponibile per chiunque importi 'app_resources'.
# Nota: La classe AppCache contiene l'istanza di AppConfigs e le istanze di FileConfigs.
GLOBAL_CACHE = AppCache()