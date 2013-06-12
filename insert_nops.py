# This script inserts variable number of no-op instructions before and after all functions
# before compiling the code to a binary
# Author: Murtaza Munaim
# External Requirements: Clang 

import argparse, sys, os, shlex, subprocess
import llvm, llvm.core

CLANG = "clang -emit-llvm -o %s -c %s"
NATIVE_ASM = "llc %s"
NATIVE_BIN = "gcc %s -o %s"
KRYP_BASE = "kryp"
def llvm_test():
    llvm.test()

def exec_cmd(base, args=()):
    exec_str = base % args
    sargs = shlex.split(exec_str)
    p = subprocess.Popen(sargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return (stdout + stderr, p.returncode)

def do_nop(mod):
    return

def nop_main(src_file):
    print >>sys.stderr, src_file
    llvm_ir = os.path.splitext(src_file)[0] + ".bc"
    print >>sys.stderr, exec_cmd(CLANG, (llvm_ir, src_file))
    with open(llvm_ir) as f:
        kryp = llvm.core.Module.from_bitcode(f)
    do_nop(kryp)
    kryp_bc = KRYP_BASE + ".bc"
    with open(kryp_bc, "w") as f:
        kryp.to_bitcode(f)
    print >>sys.stderr, exec_cmd(NATIVE_ASM, kryp_bc)
    llvm_asm = KRYP_BASE + ".s"
    bin_out = KRYP_BASE + ".out"
    print >>sys.stderr, exec_cmd(NATIVE_BIN, (llvm_asm, bin_out))
    print >>sys.stderr, exec_cmd("ls -al %s", bin_out)
    print >>sys.stderr, exec_cmd("./" + bin_out)
    return 
        
def main():
    parser = argparse.ArgumentParser(description="Add nops to opcodes and compile .c")
    parser.add_argument('finput', help='Source file to analyze')
    parser.add_argument('-t', dest='test', action="store_true", 
                        help='enable llvm test mode', required=False, default=False)
    args = parser.parse_args()

    if not os.path.isfile(args.finput):
        print >>sys.stderr, "Source file does not exist, try again"
        return
    if args.test:
        llvm_test()
    else:
        nop_main(args.finput)


if __name__ == "__main__":
    main()