from typing import TypeVar, TypeAlias, Sequence, Hashable, Callable

import overpy
import pydantic

from render_map import mapping

T = TypeVar("T")


def choose_item_from_list(list_: Sequence[T], criterion: Hashable) -> T:
    """Choose an item in such a way that it is fully deterministic and reproducible. The items must also be chosen uniformly.

    This is done by effectively using a poor-man's hash function with a co-domain of the length of the list.

    Args:
        list_: The list to choose from.
        criterion: The criterion to choose the item by.

    Returns:
        An item from the list.

    Raises:
        ValueError: If the list is empty.
    """
    if len(list_) == 0:
        raise ValueError("List must not be empty.")

    index = hash(criterion) % len(list_)
    return list_[index]
