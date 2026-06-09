"""
Persistence layer for user-defined district group mappings.
Saves/loads a flat { original_name: custom_group_name } dict as JSON.
"""

import json
import os
import sys

_FILENAME = 'district_mappings.json'


def _get_path() -> str:
    """Return the absolute path to the mappings JSON file."""
    if hasattr(sys, '_MEIPASS'):          # PyInstaller bundle
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, _FILENAME)


def load_mappings() -> dict:
    """
    Load saved district rename mappings from disk.

    Returns
    -------
    dict
        ``{ original_district_name: custom_group_name }``
        Empty dict if no file exists or the file is unreadable.
    """
    path = _get_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as exc:
        print(f'[district_names] Warning: could not read mappings – {exc}')
        return {}
    

def save_mappings(mappings: dict) -> None:
    """
    Persist ``{ original_district_name: custom_group_name }`` to disk.
    Passing an empty dict removes all custom names.
    """
    path = _get_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)
    except OSError as exc:
        print(f'[district_names] Warning: could not write mappings – {exc}')


def reset_mappings() -> None:
    """Delete all saved mappings from disk."""
    path = _get_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError as exc:
            print(f'[district_names] Warning: could not delete mappings – {exc}')


def apply_mappings(df, mappings: dict):
    """
    Return a copy of *df* with the ``'District'`` column renamed per *mappings*.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``'District'`` column.
    mappings : dict
        ``{ original_district_name: custom_group_name }``
    """
    if not mappings:
        return df
    out = df.copy()
    out['District'] = out['District'].map(lambda d: mappings.get(d, d))
    return out