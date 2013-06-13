# This script inserts variable number of no-op instructions before and after all functions
# before compiling the code to a binary
# source->bitcode->llvmpy->bitcode->exec
# Author: Murtaza Munaim(2013)
# External Requirements: clang, llc, gcc, along with llvmpy 0.11.2 requirements

import argparse, sys, os, shlex, subprocess
from llvm import *
from llvm.core import *

CLANG = "clang -emit-llvm -o %s -c %s"
NATIVE_ASM = "llc -O%d %s"
NATIVE_BIN = "gcc %s -o %s"
KRYP_BASE = "kryp"
OPT = 0

def llvm_test():
    llvm.test()

def exec_cmd(base, args=()):
    exec_str = base % args
    sargs = shlex.split(exec_str)
    p = subprocess.Popen(sargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return (stdout + stderr, p.returncode)

def do_nop(mod):
    print_mod_funcs(mod)
    
def src_to_llvm(src):
    llvm_ir = os.path.splitext(src)[0] + ".bc"
    exec_cmd(CLANG, (llvm_ir, src))
    with open(llvm_ir) as f:
        mod= llvm.core.Module.from_bitcode(f)
    os.remove(llvm_ir)
    return mod

def llvm_to_bin(mod, outputb):
    fbc = outputb + ".bc"
    with open(fbc, "w") as f:
        mod.to_bitcode(f)
    exec_cmd(NATIVE_ASM, (OPT, fbc))
    llvm_asm = outputb + ".s"
    bin_out = outputb + ".out"
    exec_cmd(NATIVE_BIN, (llvm_asm, bin_out))
    os.remove(llvm_asm)
    os.remove(fbc)
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
    llvm_to_bin(kryp, KRYP_BASE)
    return 
        
def main():
    global OPT
    parser = argparse.ArgumentParser(description="Add nops to opcodes and compile .c")
    parser.add_argument('finput', help='Source file to analyze')
    parser.add_argument('-i', dest='insert', action="store", 
                        help='src file to get function stubs from', required=False, default="modify.c")
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
    #print >>sys.stderr, OPT
    if args.test:
        llvm_test()
    else:
        nop_main(args.finput, args.insert)


if __name__ == "__main__":
    main()
