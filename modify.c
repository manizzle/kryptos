/*    This file is part of Kryptos
      
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
      
      Set of packer functions to be used by Kryptos
      Author: Murtaza Munaim(2013)
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <stdint.h>

#define KEYLEN 16

int pack(uint32_t addr, uint32_t len, uint8_t key[KEYLEN]) {
    void *page = (void *) ((unsigned long) (addr) & ~(getpagesize() - 1));
    uint8_t *buf = (uint8_t*)addr;
    int ctr = 0, kctr = 0;
    /* mark the code section we are going to overwrite as writable.  */
    mprotect(page, getpagesize(), PROT_READ | PROT_WRITE | PROT_EXEC);
    /* Simple Packer code */ 
    for (ctr = 0; ctr < len; ctr++) {
        buf[ctr] = buf[ctr] ^ key[kctr];
        kctr = (kctr + 1 ) % KEYLEN;
    }
}
