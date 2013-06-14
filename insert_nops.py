'''    This file is part of Kryptos

    Kryptos is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Kryptos is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Kryptos.  If not, see <http://www.gnu.org/licenses/>.

This script inserts variable number of no-op instructions 
before and after all functions before compiling the code to a binary
source->bitcode->llvmpy->bitcode->exec
Author: Murtaza Munaim(2013)
External Requirements: libbfd.so, clang, llc, gcc, along with llvmpy 0.11.2 requirements
'''

import argparse, sys, os, shlex, subprocess
from llvm import *
from llvm.core import *
import llvmpy
from ctypes import *

CLANG = "clang -emit-llvm -o %s -c %s"
NATIVE_ASM = "llc -O%d %s"
NATIVE_BIN = "gcc %s -o %s"
KRYP_BASE = "kryp"
OPT = 0
BFD = ""

def open_bfd():
    bfd = None
    for f in os.listdir(BFD):
        if "libbfd" in f and ".so" in f:
            bfd = CDLL(os.path.join(BFD, f))
            break
    if not bfd: 
        return bfd
    return bfd

def llvm_test():
    llvm.test()

def exec_cmd(base, args=()):
    exec_str = base % args
    sargs = shlex.split(exec_str)
    p = subprocess.Popen(sargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return (stdout + stderr, p.returncode)

def src_to_llvm(src):
    llvm_ir = os.path.splitext(src)[0] + ".bc"
    x = exec_cmd(CLANG, (llvm_ir, src))
    if x[1] != 0:
        print >>sys.stderr, x[0]
        raise ValueError("src -> clang -> llvm failed")
    with open(llvm_ir) as f:
        mod= llvm.core.Module.from_bitcode(f)
    os.remove(llvm_ir)
    return mod

def llvm_to_bin(mod, outputb):
    fbc = outputb + ".bc"
    with open(fbc, "w") as f:
        mod.to_bitcode(f)
    x = exec_cmd(NATIVE_ASM, (OPT, fbc))
    if x[1] != 0:
        print >>sys.stderr, x[0]
        raise ValueError("llvm -> llc -> native assembly")
    llvm_asm = outputb + ".s"
    bin_out = outputb + ".out"
    print llvm_asm, bin_out
    x = exec_cmd(NATIVE_BIN, (llvm_asm, bin_out))
    if x[1] != 0:
        print >>sys.stderr, x[0]
        raise ValueError("native assembly -> native assembler -> native code failed")
    os.remove(llvm_asm)
    os.remove(fbc)
    return bin_out
    #print >>sys.stderr, exec_cmd("ls -al %s", bin_out)
    #print >>sys.stderr, exec_cmd("./" + bin_out)[0]

def print_mod_funcs(mod):
    print "[+] Module: %s " % (mod.id)
    for f in mod.functions:
        print "\t[+] Function: %s" % f.name
        print "\t[+] Num Args: %d" % len(f.args)
        print "\t[+] Num BasicBlocks: %d" % f.basic_block_count
        if f.basic_block_count:
            print "\t[+] First BasicBlock: %s" % str(f.entry_basic_block)
        else:
            print "\t[+] No Blocks\n"
        
def nop_main(src_file, insert_file):
    #print >>sys.stderr, src_file
    # Add in stub functions
    kryp = src_to_llvm(src_file)
    insert_mod = src_to_llvm(insert_file)
    kryp.link_in(insert_mod)
    do_nop(kryp)
    binpath = llvm_to_bin(kryp, KRYP_BASE)    
    bfd = open_bfd()
    return 
        
def main():
    global OPT
    global BFD
    parser = argparse.ArgumentParser(description="Add nops to opcodes and compile .c")
    parser.add_argument('finput', help='Source file to analyze')
    parser.add_argument('-i', dest='insert', action="store", 
                            help='src file to get function stubs from', required=False, default="modify.c")
    parser.add_argument('-b', dest='bfdpath', action="store", 
                        help='path to look for libbfd for ctypes loading', required=False, default="/usr/local/lib/")
    parser.add_argument('-t', dest='test', action="store_true", 
                        help='enable llvm test mode', required=False, default=False)
    parser.add_argument('-l', dest='opt', action="store", 
                        help='set llc optimization', required=False, default=0)
    args = parser.parse_args()

    if not os.path.isfile(args.finput):
        print >>sys.stderr, "Source file does not exist, try again"
        return
    #print >>sys.stderr, args.opt
    if int(args.opt) >= 0 and int(args.opt) <= 3:
        OPT = int(args.opt)
    else:
        OPT = 0
    BFD = args.bfdpath
    #print >>sys.stderr, OPT
    if args.test:
        llvm_test()
    else:
        nop_main(args.finput, args.insert)

def do_nop(mod):
    for func in mod.functions:
        # Skip past main packer function
        if func.name == "pack":
            continue
        if not func.basic_blocks:
            continue
        entry = func.entry_basic_block
        pack_stub = entry.insert_before("pack_stub")
        print >>sys.stderr, pack_stub
        builder = llvm.core.Builder.new(pack_stub)
        builder.branch(entry)
        print >>sys.stderr, func.basic_block_count
        print >>sys.stderr, func
    
if __name__ == "__main__":
    main()
