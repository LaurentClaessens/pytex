from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pytex.src.options import Options


def get_options()->'Options':
    from pytex.src.options import Options
    return Options.get_instance()
