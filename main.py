#!/usr/bin/env python3
import sys 

class SimdPU:
    gprs = [[0,0,0,0]]*4
    swizzle_state = [[0,0,0,0]]*3
    memory = [0]*1024
    fixed_shift = 0
    reg_mask = 0b11

    def __init__(self):
        for i in range(4):
            self.gprs[i] = [0, 0, 0, 0]

        for i in range(3):
            self.swizzle_state[i] = [0, 1, 2, 3]
        return
        
    def set_mem(self, mem_list):
        for i in range(len(mem_list)):
            self.memory[i] = mem_list[i]

    def swizzle(self, reg, vec):
        result = [0,0,0,0]
        result[0] = vec[self.swizzle_state[reg][0]]
        result[1] = vec[self.swizzle_state[reg][1]]
        result[2] = vec[self.swizzle_state[reg][2]]
        result[3] = vec[self.swizzle_state[reg][3]]
        return result

    def vec_add(self, vecA, vecB):
        result = [0,0,0,0]
        result[0] = (vecA[0] + vecB[0]) & 0xFFFF
        result[1] = (vecA[1] + vecB[1]) & 0xFFFF
        result[2] = (vecA[2] + vecB[2]) & 0xFFFF
        result[3] = (vecA[3] + vecB[3]) & 0xFFFF
        return result

    def vec_sub(self, vecA, vecB):
        result = [0,0,0,0]
        result[0] = (vecA[0] - vecB[0]) & 0xFFFF
        result[1] = (vecA[1] - vecB[1]) & 0xFFFF
        result[2] = (vecA[2] - vecB[2]) & 0xFFFF
        result[3] = (vecA[3] - vecB[3]) & 0xFFFF
        return result

    def vec_dot(self, vecA, vecB):
        result = [0,0,0,0]
        result[0] = vecA[0]*vecB[0] + vecA[1]*vecB[1] + vecA[2]*vecB[2] + vecA[3]*vecB[3]
        return result

    def vec_mul(self, vecA, vecB):
        result = [0,0,0,0]
        result[0] = ((vecA[0] * vecB[0]) >> self.fixed_shift) & 0xFFFF
        result[1] = ((vecA[1] * vecB[1]) >> self.fixed_shift) & 0xFFFF
        result[2] = ((vecA[2] * vecB[2]) >> self.fixed_shift) & 0xFFFF
        result[3] = ((vecA[3] * vecB[3]) >> self.fixed_shift) & 0xFFFF
        return result

    def run_prg(self, prg):
        for line in prg.splitlines():
            vals = line.split()
            if vals[0] == "add":
                dst = int(vals[1])
                srcA = int(vals[2])
                srcB = int(vals[3])
                self.gprs[dst] = self.swizzle(0, self.vec_add(self.swizzle(1, self.gprs[srcA]),
                                                              self.swizzle(2, self.gprs[srcB])))
            elif vals[0] == "addi":
                dst = int(vals[1]) & self.reg_mask
                srcA = int(vals[2]) & self.reg_mask
                imm = int(vals[3]) & 0b111111
                self.gprs[dst] = self.swizzle(0, self.vec_add(self.swizzle(1, self.gprs[srcA]),
                                                              self.swizzle(2, [imm, 0, 0, 0])))
            if vals[0] == "sub":
                dst = int(vals[1]) & self.reg_mask
                srcA = int(vals[2]) & self.reg_mask
                srcB = int(vals[3]) & self.reg_mask
                self.gprs[dst] = self.swizzle(0, self.vec_sub(self.swizzle(1, self.gprs[srcA]),
                                                              self.swizzle(2, self.gprs[srcB])))
            elif vals[0] == "mul":
                dst = int(vals[1]) & self.reg_mask
                srcA = int(vals[2]) & self.reg_mask
                srcB = int(vals[3]) & self.reg_mask
                self.gprs[dst] = self.swizzle(0, self.vec_mul(self.swizzle(1, self.gprs[srcA]),
                                                              self.swizzle(2, self.gprs[srcB])))
            elif vals[0] == "dot":
                dst = int(vals[1]) & self.reg_mask
                srcA = int(vals[2]) & self.reg_mask
                srcB = int(vals[3]) & self.reg_mask
                self.gprs[dst] = self.swizzle(0, self.vec_dot(self.swizzle(1, self.gprs[srcA]),
                                                              self.swizzle(2, self.gprs[srcB])))
            elif vals[0] == "fshift":
                amt = int(vals[1]) & 0b1111
                self.fixed_shift = amt
            elif vals[0] == "swizzle":
                reg = int(vals[1]) & self.reg_mask
                swizA = int(vals[2]) & self.reg_mask
                swizB = int(vals[3]) & self.reg_mask
                swizC = int(vals[4]) & self.reg_mask
                swizD = int(vals[5]) & self.reg_mask
                self.swizzle_state[reg][0] = swizA
                self.swizzle_state[reg][1] = swizB
                self.swizzle_state[reg][2] = swizC
                self.swizzle_state[reg][3] = swizD
            elif vals[0] == "lvec":
                reg = int(vals[1]) & self.reg_mask
                addr = int(vals[2])
                inc = int(vals[3])
                self.gprs[reg][0] = self.memory[addr + 0*inc]
                self.gprs[reg][1] = self.memory[addr + 1*inc]
                self.gprs[reg][2] = self.memory[addr + 2*inc]
                self.gprs[reg][3] = self.memory[addr + 3*inc]
            elif vals[0] == "rst":
                reg = int(vals[1]) & self.reg_mask
                self.gprs[reg][0] = 0
                self.gprs[reg][1] = 0
                self.gprs[reg][2] = 0
                self.gprs[reg][3] = 0
            elif vals[0] == "done":
                break

    def print_state(self):
        print("GPRs:")
        for i in range(len(self.gprs)):
            print("    GPR{}: {}".format(i, self.gprs[i]))


def main():
    if len(sys.argv) < 2:
        print("Please pass file name in")
        return 0
        
    proc = SimdPU()
    prg = ""
    f = open(sys.argv[1])
    prg = f.read()
    f.close()
    
    if len(sys.argv) >= 3:
        mem_list = []
        f = open(sys.argv[2])
        for line in f:
            mem_list.append(int(line.strip()))
        f.close()
        
        proc.set_mem(mem_list)

    proc.run_prg(prg)
    proc.print_state()

    return 0

if __name__ == "__main__":
    sys.exit(main())
