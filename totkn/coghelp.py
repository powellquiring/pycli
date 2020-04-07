# import cog


def cogout(s):
    #    cog.out(s)
    print(s)


def get_type_name(typ) -> str:
    if hasattr(typ, "__name__"):
        return typ.__name__
    s = str(typ)
    return s


def class_props(c):
    cogout(
        f"""
    @property
    def props(self) -> Dict[str, Any]:
        return self._props
"""
    )
    for (prop, type_required) in c._props.items():
        typ = type_required[0]
        # required = type_required[1]
        type_name = get_type_name(typ)
        out = f"""
    @property
    def {prop}(self) -> {type_name}:
        return self._{prop}
    @{prop}.setter
    def {prop}(self, value: {type_name}):
        self._{prop} = value
"""
        cogout(out)


if __name__ == "__main__":
    import t

    class_props(t.TT)
