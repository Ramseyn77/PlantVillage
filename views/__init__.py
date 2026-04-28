from .accueil import show as accueil_page
from .a_propos import show as apropos_page
from .reconnaissance import show as reconnaissance_page
from .historique import show as historique_page
from .connexion import show as connexion_page  
from .champ_page import show as champ_page
from .culture_page import show as culture_page
from .analyse import show as analyse_page

__all__ = [
    "accueil_page",
    "apropos_page",
    "reconnaissance_page",
    "historique_page",
    "connexion_page",
    "champ_page",
    "culture_page",
    "analyse_page"
]