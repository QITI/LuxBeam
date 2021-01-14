import io


class _Counter(object):
    def __init__(self):
        self.count = 0

    def __call__(self):
        r = self.count
        self.count += 1
        return r

    def reset(self):
        self.count = 0


class LuxbeamSequencer(object):
    def __init__(self):
        self.command = []
        self.used_labels = []
        self.const_vars = dict()

        self._loop_counter = _Counter()
        self._var_counter = _Counter()

    def __str__(self):
        return self.dumps()

    def _check_inum(self, inum):
        if isinstance(inum, int):
            if 0 <= inum <= 65535:
                pass
            else:
                raise ValueError("inum is out of range (0 <= inum <= 65535)")
        else:
            raise TypeError("inum must be an integer.")

    def add_line(self, command, parameters):
        self.command.append([command, *parameters])

    def dumps(self):
        f = io.StringIO()
        for value, var in self.const_vars.items():
            assert isinstance(value, int)
            assert isinstance(var, LuxbeamSequencerVariable)
            f.write("AssignVar {0} {1} 1".format(var.var, value))
            f.write('\n')
        for line in self.command:
            f.write(' '.join(line))
            f.write('\n')
        return f.getvalue()

    def clear(self):
        raise NotImplementedError("Currently not implemented")

    def _assign_const_var(self, value):
        try:
            var = self.const_vars[value]
        except KeyError:
            var = LuxbeamSequencerVariable(self, "ConstVar{0}".format(value))
            self.const_vars[value] = var
        return var

    def reset_global(self, wait_for=1):
        self.add_line("ResetGlobal", [str(wait_for)])

    def assign_var(self, value=0, var=None, wait_for=1):
        if var is None:
            var = "Var{0}".format(self._var_counter())

        self.add_line("AssignVar", [var, str(value), str(wait_for)])
        var = LuxbeamSequencerVariable(self, var)
        return var

    def load_global(self, inum, wait_for=400):
        if isinstance(inum, int):
            inum = self._assign_const_var(inum)
        if not isinstance(inum, LuxbeamSequencerVariable):
            raise TypeError
        self.add_line("LoadGlobal", [inum.var, str(wait_for)])

    def label(self, label, wait_for=1):
        if not isinstance(label, str):
            raise ValueError
        self.add_line("Label", [label, str(wait_for)])

    def jump(self, label, wait_for=1):
        if not isinstance(label, str):
            raise ValueError
        self.add_line("Jump", [label, str(wait_for)])

    def jump_if(self, var_a, operator, var_b, label, wait_for=1):
        if not isinstance(label, str):
            raise ValueError
        if not isinstance(var_a, LuxbeamSequencerVariable):
            raise TypeError
        if isinstance(var_b, int):
            var_b = self._assign_const_var(var_b)
        elif not isinstance(var_b, LuxbeamSequencerVariable):
            raise TypeError
        self.add_line("JumpIf", [var_a.var, operator, var_b.var, label, str(wait_for)])

    def trig(self, mode, source, timeout):
        self.add_line("Trig", [str(mode), str(source), str(timeout)])

    def jump_loop_iter(self):
        return LuxbeamSequencerJumpLoopIterator(self)

    def range_loop_iter(self, a, b=None, step=1):
        if b is None:
            start = 0
            end = a
        else:
            start, end = a, b
        return LuxbeamSequencerRangeLoopIterator(self, start, end, step)

    def add(self, var_a, value_or_var_b, wait_for=1):
        if not isinstance(var_a, LuxbeamSequencerVariable):
            raise TypeError
        if isinstance(value_or_var_b, int):
            self.add_line("Add", [var_a.var, str(value_or_var_b), str(wait_for)])
        elif isinstance(value_or_var_b, LuxbeamSequencerVariable):
            self.add_line("Add", [var_a.var, value_or_var_b.var, str(wait_for)])
        else:
            raise TypeError


class LuxbeamSequencerVariable(object):
    def __init__(self, parent: LuxbeamSequencer, var):
        self.var = var
        self.parent = parent


class LuxbeamSequencerJumpLoopIterator(object):
    def __init__(self, parent: LuxbeamSequencer):
        self.parent = parent

    def __iter__(self):
        label = "Loop{0}".format(self.parent._loop_counter())
        self.parent.label(label)
        yield label
        self.parent.jump(label)


class LuxbeamSequencerRangeLoopIterator(object):
    def __init__(self, parent: LuxbeamSequencer, start=0, end=1, step=1):
        if not end > start:
            raise ValueError
        self.parent = parent
        self.start = start
        self.end = end
        self.step = step

    def __iter__(self):
        label = "Loop_{0}".format(self.parent._loop_counter())
        var = self.parent.assign_var(self.start)
        self.parent.label(label)
        yield label, var
        self.parent.add(var, 1)
        self.parent.jump_if(var, '<', self.end, label, 1)
