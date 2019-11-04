from enum import Enum


class Phases(Enum):
    BEGINNING_PHASE = 1
    UNTAP_STEP = 2
    UPKEEP_STEP = 3
    DRAW_STEP = 4
    MAIN_PHASE_PRE_COMBAT = 5
    COMBAT_PHASE = 6
    BEGINNING_OF_COMBAT_STEP = 7
    DECLARE_ATTACKERS_STEP = 8
    DECLARE_BLOCKERS_STEP = 9
    DECLARE_BLOCKERS_STEP_509_2 = 10
    COMBAT_DAMAGE_STEP_510_1c = 11
    COMBAT_DAMAGE_STEP = 12
    END_OF_COMBAT_STEP = 13
    MAIN_PHASE_POST_COMBAT = 14
    ENDING_PHASE = 15
    END_STEP = 16
    CLEANUP_STEP = 17

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]
