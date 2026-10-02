import html
import math
import re

from aoe2.aoe2_civ_icon import aoe2_civilization_icon
from aoe2.aoe2_icon_info import AOE2_NOTE_TOKEN_COMPAT
from common.build_order_tools import check_valid_faction, FieldDefinition, check_valid_steps



def normalize_buildorderguide_notes(build_orders: list) -> None:
    """Normalize notes from buildorderguide.com's newer export format.

    Iterates build order dicts (self.build_orders), walking each BO's
    'build_order' step list to normalize note strings in place.

    Parameters
    ----------
    build_orders   List of build order dicts, each with a 'build_order' key
                   containing the list of step dicts.
    """
    if not AOE2_NOTE_TOKEN_COMPAT:
        return
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(token) for token in sorted(AOE2_NOTE_TOKEN_COMPAT, key=len, reverse=True)) + r")\b"
    )

    def _replace(match):
        return AOE2_NOTE_TOKEN_COMPAT[match.group(1)]

    for bo in build_orders:
        for step in bo.get("build_order", []):
            notes = step.get("notes")
            if not notes:
                continue
            # HTML 转义还原（&gt; → > 等）：部分流程编辑器/网站导出时会转义特殊字符
            notes = [html.unescape(note) if isinstance(note, str) else note for note in notes]
            step["notes"] = [
                pattern.sub(_replace, note) if isinstance(note, str) else note for note in notes
            ]


def check_valid_aoe2_build_order(data: dict, bo_name_msg: bool = False) -> (bool, str):
    """Check if a build order is valid for AoE2.

    Parameters
    ----------
    data           Data of the build order JSON file.
    bo_name_msg    True to add the build order name in the error message.

    Returns
    -------
    True if valid build order, False otherwise.
    String indicating the error (empty if no error).
    """
    bo_name_str: str = ''
    try:
        if bo_name_msg:
            bo_name_str = data['name'] + ' | '

        # Check correct civilization
        valid_faction, faction_msg = check_valid_faction(
            data,
            bo_name_str,
            faction_name='civilization',
            factions_list=aoe2_civilization_icon,
            requested=False,
            any_valid=True,
        )
        if not valid_faction:
            return False, faction_msg

        fields = [
            FieldDefinition('villager_count', 'integer', True),
            FieldDefinition('age', 'integer', True, None, [-math.inf, 4]),
            FieldDefinition('wood', 'integer', True, 'resources'),
            FieldDefinition('food', 'integer', True, 'resources'),
            FieldDefinition('gold', 'integer', True, 'resources'),
            FieldDefinition('stone', 'integer', True, 'resources'),
            FieldDefinition('builder', 'integer', False, 'resources'),
            FieldDefinition('notes', 'array of strings', True),
            FieldDefinition('time', 'string', False),
        ]

        return check_valid_steps(data, bo_name_str, fields)

    except KeyError as err:
        return False, bo_name_str + f'Wrong JSON key: {err}.'

    except Exception as err:
        return False, bo_name_str + str(err)


def aoe2_build_order_sorting(elem: dict) -> int:
    """Sorting key used to order the build orders:
       civilizations set as 'Any'/'any'/'Generic' (or not specified) appear at the end.

    Parameters
    ----------
    elem    Build order data to analyze.

    Returns
    -------
    Key value for sorting.
    """
    return 1 if (('civilization' not in elem) or (elem['civilization'] in ['any', 'Any', 'Generic'])) else 0
