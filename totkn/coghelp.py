def testing() -> bool:
    return __name__ == "__main__"


if not testing():
    import cog


def cogout(s):
    if testing():
        print(s)
    else:
        cog.out(s)


def get_type_name(typ) -> str:
    """The code generated is put in the totkn module (totkn.py) so it can not reference itself with
    a fully qualified name"""
    if hasattr(typ, "__name__"):
        return typ.__name__
    s = str(typ)
    return s.replace("totkn.", "")


def generate_setter(typ) -> bool:
    """ typing.Lists do not need setters"""
    type_name = get_type_name(typ)
    return not type_name.startswith("typing.List")


def class_props(c):
    for (prop, type_required) in c._props.items():
        typ = type_required[0]
        # required = type_required[1]
        type_name = get_type_name(typ)
        out = f"""
    @property
    def {prop}(self) -> {type_name}:
        return self._{prop}
"""
        if generate_setter(typ):
            out += f"""
    @{prop}.setter
    def {prop}(self, value: {type_name}):
        self._{prop} = value
    """
        cogout(out)


if __name__ == "__main__":
    import t

    class_props(t.TT)
