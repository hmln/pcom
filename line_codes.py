from itertools import cycle

from bitstring import Bits


def tick(it):
    for x in it:
        yield (1, x)
        yield (0, x)


class BinaryData:

    def __init__(self, *args, **kwargs):
        self.set_data(*args, **kwargs)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def set_data(self, *args, **kwargs):
        self.data = Bits(*args, **kwargs)

    def nrz_l(self):
        return (1 if x else -1 for x in self)

    def nrz_m(self):
        return (1 if x else -1 for x in self.marca())

    def nrz_s(self):
        return (1 if x else -1 for x in self.espaco())

    def unipolar_rz(self):
        return (clock & bit for clock, bit in tick(self))

    def polar_rz(self):
        polar = (1 if x else -1 for x in self)
        return (clock * bit for clock, bit in tick(polar))

    def ami(self):
        bit = cycle((1, -1))
        for x in self:
            if x:
                yield next(bit)
            else:
                yield 0

    def cmi(self):
        bit = cycle((1, -1))
        for x in self:
            if x:
                b = next(bit)
                yield b
                yield b
            else:
                yield -1
                yield 1

    def hdb3(self):
        data = self.data.bin
        parity = -1  # primeira substituicao sempre é por 000V
        last = -1
        hdb3 = []
        for segment in data.split('0000'):
            for x in segment:
                if x == '1':
                    last = -last
                    hdb3.append(last)
                    parity = 1 - parity
                else:
                    hdb3.append(0)
            if parity == 0:
                last = -last
                hdb3.extend([last, 0, 0, last])
            else:  # parity =1 ou primeira substituicao
                hdb3.extend([0, 0, 0, last])
            parity = 0
        del hdb3[-4:]
        return hdb3

    def manchester(self, IEEE=None):
        if IEEE:
            return (2 * (clock ^ bit) - 1 for clock, bit in tick(self))
        return (1 - 2 * (clock ^ bit) for clock, bit in tick(self))

    def dif_manchester(self, last=1):
        for x in self:
            if x == 1:
                yield -1 * last
                yield last
            else:
                last = -1 * last
                yield last
                yield last

    def mlt3(self):
        last = 0
        bit = cycle((1, 0, -1, 0))
        for x in self:
            if x:
                last = next(bit)
            yield last

    def miller(self):
        last = -1
        preceded_by_zero = 0
        for x in self:
            if x:
                yield last
                last = -last
                yield last
                preceded_by_zero = 0
            else:
                if preceded_by_zero:
                    last = -last
                yield last
                yield last
                preceded_by_zero = 1

    def marca(self, change=1, start=1):
        if self[0] == change:
            last_bit = 1 - start
        else:
            last_bit = start

        for bit in self:
            if bit == change:
                last_bit = 1 - last_bit
                yield last_bit
            else:
                yield last_bit

    def espaco(self):
        return self.marca(change=0, start=0)
