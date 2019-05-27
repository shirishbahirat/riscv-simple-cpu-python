import re
import sys


class inst_set_arch(object):

    def __init__(self):

        self._r = '0110011'
        self._i = '0010011'
        self._l = '0000011'
        self._s = '0100011'
        self._b = '1100011'
        self._j = '1101111'

        self._rg = '0000000'
        self._ra = '0100000'

        self._add = '000'
        self._sub = '000'
        self._sll = '001'
        self._slt = '010'
        self._sltu = '011'
        self._xor = '100'
        self._srl = '101'
        self._sra = '101'
        self._or = '110'
        self._and = '111'

        self._lsb = '000'
        self._lsh = '001'
        self._lsw = '010'

        self._lbu = '100'
        self._lhu = '101'

        self._beq = '000'


class inst_decode(inst_set_arch):

    def __init__(self, fname):
        super().__init__()
        self.fname = fname

    def reg_to_num(self, reg):
        return int(reg[1:3])

    def check_inst_type(self, inst):
        if ((inst == 'add') or (inst == 'sub') or (inst == 'sll')
            or (inst == 'slt') or (inst == 'sltu') or (inst == 'xor')
            or (inst == 'srl') or (inst == 'sra') or (inst == 'or')
                or (inst == 'and')):
            return 'r_type'

        if ((inst == 'addi') or (inst == 'slti') or (inst == 'sltiu')
            or (inst == 'xori') or (inst == 'ori') or (inst == 'slli')
                or (inst == 'srli') or (inst == 'srai')):
            return 'i_type'

        if (inst == 'slli') or (inst == 'srli') or (inst == 'srai'):
            return 'is_type'

        if ((inst == 'lb') or (inst == 'lh') or (inst == 'lw')
                or (inst == 'lbu') or (inst == 'lhu')):
            return 'l_type'

        if (inst == 'sb') or (inst == 'sh') or (inst == 'sw'):
            return 's_type'

        if (inst == 'beq'):
            return 'b_type'

        if (inst == 'jal'):
            return 'j_type'

    def check_functio_type(self, inst):
        if ((inst == 'add') or (inst == 'sll') or (inst == 'slt')
            or (inst == 'sltu') or (inst == 'xor') or (inst == 'srl')
                or (inst == 'or') or (inst == 'and')):
            return 'gen'
        elif (inst == 'sub') or (inst == 'sra'):
            return 'unique'

    def j_code_decode(self, line):
        mcode = int(self._j, 2)
        mcode = mcode | (self.reg_to_num(line[1]) << 7)
        imm_decode = int(line[3])
        imm_dec_lo = int('11111111000000000000', 2) & imm_decode
        imm_dec_lo = imm_dec_lo >> 12
        mcode = mcode | imm_dec_lo << 12

        imm_dec_hi = int('11111111110', 2) & imm_decode
        imm_dec_11 = int('100000000000', 2) & imm_decode
        imm_dec_20 = int('100000000000000000000', 2) & imm_decode

        mcode = mcode | (imm_dec_11 << 20)
        mcode = mcode | (imm_dec_hi << 21)
        mcode = mcode | (imm_dec_20 << 31)

        return mcode

    def r_code_decode(self, line):
        mcode = int(self._r, 2)
        mcode = mcode | (self.reg_to_num(line[1]) << 7)
        mcode = mcode | (self.reg_to_num(line[2]) << 15)
        mcode = mcode | (self.reg_to_num(line[3]) << 20)
        return mcode

    def s_code_decode(self, line):
        mcode = int(self._s, 2)
        mcode = mcode | (int(line[1]) << 7)
        mcode = mcode | (self.reg_to_num(line[2]) << 15)
        mcode = mcode | (self.reg_to_num(line[3]) << 20)
        return mcode

    def i_code_decode(self, line):
        mcode = int(self._i, 2)
        mcode = mcode | (self.reg_to_num(line[1]) << 7)
        mcode = mcode | (self.reg_to_num(line[2]) << 15)
        return mcode

    def l_code_decode(self, line):
        mcode = int(self._l, 2)
        mcode = mcode | (self.reg_to_num(line[1]) << 7)
        mcode = mcode | (self.reg_to_num(line[2]) << 15)
        return mcode

    def b_type_decode(self, line):
        imm_decode = int(line[3]) << 1
        imm_dec_lo = int('11110', 2) & imm_decode | (imm_dec_11 >> 11)

        imm_dec_hi = (int('11111100000', 2) & imm_decode) >> 5

        imm_dec_11 = int('100000000000', 2) & imm_decode
        imm_dec_12 = (int('1000000000000', 2) & imm_decode) >> 12

        imm_dec_hi = imm_dec_hi | (imm_dec_12 << 12)

        mcode = int(self._b, 2)
        mcode = mcode | imm_dec_lo << 7
        mcode = mcode | (self.reg_to_num(line[2]) << 15)
        mcode = mcode | (self.reg_to_num(line[3]) << 20)
        mcode = mcode | (imm_dec_hi << 20)

        return mcode

    def read_and_decode(self):
        with open(self.fname, "r") as ins:
            code = []
            machine_code = []

            for line in ins:
                line = line.rstrip()
                line = re.split(' |, ', line)
                line[0] = line[0].lower()

                if line[0][0] == '.':
                    continue
                else:
                    code.append(line)

                if self.check_inst_type(line[0]) == 'j_type':
                    mcode = self.j_code_decode(line)

                if self.check_inst_type(line[0]) == 'r_type':
                    mcode = self.r_code_decode(line)

                elif ((self.check_inst_type(line[0]) == 'i_type')
                        or (self.check_inst_type(line[0]) == 'is_type')):
                    mcode = self.i_code_decode(line)
                    mcode = mcode | (int(line[3]) << 20)

                elif (self.check_inst_type(line[0]) == 'l_type'):
                    mcode = self.l_code_decode(line)
                    mcode = mcode | (int(line[3]) << 20)

                elif (self.check_inst_type(line[0]) == 's_type'):
                    mcode = self.s_code_decode(line)
                    mcode = mcode | (int(line[3]) << 25)

                if self.check_functio_type(line[0]) == 'gen':
                    mcode = mcode | (int(self._rg, 2) << 25)
                elif self.check_functio_type(line[0]) == 'unique':
                    mcode = mcode | (int(self._ra, 2) << 25)
                else:
                    if (self.check_inst_type(line[0]) == 'is_type'):
                        if (line[0] == 'srai'):
                            mcode = mcode | (int(self._ra, 2) << 25)
                        elif (line[0] == 'slli') or (line[0] == 'srai'):
                            mcode = mcode | (int(self._rg, 2) << 25)

                if (line[0] == 'add') or (line[0] == 'addi'):
                    mcode = mcode | (int(self._add, 2) << 12)

                elif line[0] == 'sub':
                    mcode = mcode | (int(self._sub, 2) << 12)

                elif (line[0] == 'sra') or (line[0] == 'srali'):
                    mcode = mcode | (int(self._sra, 2) << 12)

                elif (line[0] == 'sll') or (line[0] == 'slli'):
                    mcode = mcode | (int(self._sll, 2) << 12)

                elif (line[0] == 'slt') or (line[0] == 'slti'):
                    mcode = mcode | (int(self._slt, 2) << 12)

                elif (line[0] == 'sltu') or (line[0] == 'sltiu'):
                    mcode = mcode | (int(self._sltu, 2) << 12)

                elif (line[0] == 'xor') or (line[0] == 'xori'):
                    mcode = mcode | (int(self._xor, 2) << 12)

                elif (line[0] == 'srl') or (line[0] == 'srli'):
                    mcode = mcode | (int(self._srl, 2) << 12)

                elif line[0] == 'sra':
                    mcode = mcode | (int(self._sra, 2) << 12)

                elif line[0] == 'or':
                    mcode = mcode | (int(self._or, 2) << 12)

                elif (line[0] == 'and') or (line[0] == 'andi'):
                    mcode = mcode | (int(self._and, 2) << 12)

                elif (line[0] == 'lb') or (line[0] == 'sb'):
                    mcode = mcode | (int(self._lsb, 2) << 12)

                elif (line[0] == 'lh') or (line[0] == 'sh'):
                    mcode = mcode | (int(self._lsh, 2) << 12)

                elif (line[0] == 'lw') or (line[0] == 'sw'):
                    mcode = mcode | (int(self._lsw, 2) << 12)

                elif (line[0] == 'lbu'):
                    mcode = mcode | (int(self._lbu, 2) << 12)

                elif (line[0] == 'lhu'):
                    mcode = mcode | (int(self._lhu, 2) << 12)

                else:
                    print('Error: undefined instruction')
                    sys.exit()

                print(f"{mcode:032b}", line)
                machine_code.append(mcode)


def main():

    compile = inst_decode('program.txt')
    compile.read_and_decode()


main()
