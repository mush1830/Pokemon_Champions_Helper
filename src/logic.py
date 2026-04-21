from dataclasses import dataclass, field
from typing import Optional
from src.data_manager import PokemonDataManager
from src.type_chart import format_weaknesses


@dataclass
class ComparisonResult:
    my_name: Optional[str]
    my_speed: Optional[int]
    opp_name: Optional[str]
    opp_speed: Optional[int]
    # "my" | "opponent" | "tie" | None
    faster: Optional[str]
    my_raw_ocr: str = ""
    opp_raw_ocr: str = ""
    my_weaknesses: str = "-"
    opp_weaknesses: str = "-"
    my_megas: list = field(default_factory=list)
    opp_megas: list = field(default_factory=list)


class SpeedComparator:
    def __init__(self, data_manager: PokemonDataManager):
        self.data_manager = data_manager

    def compare(
        self,
        my_name: Optional[str],
        opp_name: Optional[str],
        my_raw: str = "",
        opp_raw: str = "",
    ) -> ComparisonResult:
        my_speed = self.data_manager.get_speed(my_name) if my_name else None
        opp_speed = self.data_manager.get_speed(opp_name) if opp_name else None

        faster = None
        if my_speed is not None and opp_speed is not None:
            if my_speed > opp_speed:
                faster = "my"
            elif opp_speed > my_speed:
                faster = "opponent"
            else:
                faster = "tie"

        my_types = self.data_manager.get_types(my_name) if my_name else None
        opp_types = self.data_manager.get_types(opp_name) if opp_name else None
        my_weak = format_weaknesses(my_types) if my_types else "-"
        opp_weak = format_weaknesses(opp_types) if opp_types else "-"

        my_megas = self.data_manager.get_megas(my_name) if my_name else []
        opp_megas = self.data_manager.get_megas(opp_name) if opp_name else []

        return ComparisonResult(
            my_name=my_name,
            my_speed=my_speed,
            opp_name=opp_name,
            opp_speed=opp_speed,
            faster=faster,
            my_raw_ocr=my_raw,
            opp_raw_ocr=opp_raw,
            my_weaknesses=my_weak,
            opp_weaknesses=opp_weak,
            my_megas=my_megas,
            opp_megas=opp_megas,
        )
