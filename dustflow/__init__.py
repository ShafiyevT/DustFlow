# -*- coding: utf-8 -*-
"""
DustFlow — shamol eroziyasi va atmosferaning changlanishini monitoring qilish
va bashoratlash uchun dasturiy majmua.

Modullar:
    grid      — hisoblash to'ri va relyefga moslashgan koordinatalar
    data      — kirish ma'lumotlarini tayyorlash
    emission  — chang emissiyasi sxemasi, II bob (2.1)-(2.12), (2.25)
    velocity  — zarrachalar harakat tezliklari va cho'kish tezligi (DustVel 2.0 yadrosi)
    solver    — ko'chish va diffuziya masalasining yechuvchisi:
                "tezkor" (II bob, 1-tartib) va "aniq" (III bob, 2-tartib)
    balance   — massa balansini nazorat qilish
    viz       — natijalarni vizuallashtirish
"""
__version__ = "2.0.0"

from .grid import Tor, relyef_yarat
from .emission import emissiya_maydoni, fraksiya_ulushlari
from .solver import Yechuvchi

__all__ = ["Tor", "relyef_yarat", "emissiya_maydoni",
           "fraksiya_ulushlari", "Yechuvchi", "__version__"]
