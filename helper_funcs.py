from collections.abc import Callable

from handcalcs import handcalc

def func_by_run_type(render_hc: bool, args: dict, Func: Callable):
    latex = None #initiate empty
    if render_hc:
        latex, vals = handcalc(override="long")(Func)(**args)
    elif not render_hc:
        vals = Func(**args)
    return latex, vals