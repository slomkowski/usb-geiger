#
# USB Geiger counter
# 2013 Michał Słomkowski
# This code is distributed under the terms of GNU General Public License version 3.0.
#
 
AVR-CC=avr-gcc
AVR-OBJCOPY=avr-objcopy
AVR-SIZE=avr-size
AVRDUDE=avrdude

OUTPUT=firmware

CPU-GCC=attiny24
CPU-AVRDUDE=t24

CFLAGS=-mmcu=$(CPU-GCC) -std=c99 -Iusbdrv -I. -Os
CFLAGS+=-Wall -Wl,--relax

# config for USB programmer
PROGRAMMER=stk500v2
PORT=avrdoper

FUSE_LOW=0xfe
FUSE_HIGH=0xd4
FUSE_EXTENDED=0xff

EXTRA_DEPS = global.h

BIN_DIR=obj

SRC_C = $(shell ls *.c usbdrv/*.c)
SRC_ASM = $(shell ls usbdrv/*.S)


.SUFFIXES:
.SUFFIXES: .h .c .o

HEADERS = $(SRC_C:%.c=%.h) 
OBJ = $(SRC_C:%.c=$(BIN_DIR)/%.o)
OBJ += $(SRC_ASM:%.S=$(BIN_DIR)/%.o)

all : $(OUTPUT).hex

directories:
	if [ ! -e $(BIN_DIR) ]; then mkdir -p $(BIN_DIR)/usbdrv; fi

# generic code
$(OUTPUT).hex : $(BIN_DIR)/$(OUTPUT).elf
	$(AVR-OBJCOPY) -O ihex $(BIN_DIR)/$(OUTPUT).elf $(OUTPUT).hex
	$(AVR-SIZE) $(OUTPUT).hex

$(BIN_DIR)/$(OUTPUT).elf : $(OBJ) 
	$(AVR-CC) $(CFLAGS) -o $(BIN_DIR)/$(OUTPUT).elf $(OBJ)

$(BIN_DIR)/main.o : main.c $(EXTRA_DEPS) directories
	$(AVR-CC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/%.o : %.c %.h $(EXTRA_DEPS) directories
	$(AVR-CC) $(CFLAGS) -c $< -o $@

# Generic rule for assembling Assembler source files:
$(BIN_DIR)/%.o : %.S
	$(AVR-CC) $(CFLAGS) -x assembler-with-cpp -c $< -o $@

run: burn

burn: $(OUTPUT).hex
	$(AVRDUDE) -c $(PROGRAMMER) -p $(CPU-AVRDUDE) -P $(PORT) -U flash:w:"$(OUTPUT).hex":a -U flash:v:"$(OUTPUT).hex":a -e

burn_fuses:
	$(AVRDUDE) -c $(PROGRAMMER) -p $(CPU-AVRDUDE) -P $(PORT) -U lfuse:w:$(FUSE_LOW):m -U hfuse:w:$(FUSE_HIGH):m -U efuse:w:$(FUSE_EXTENDED):m

clean:
	rm -rf $(OUTPUT).* $(BIN_DIR)

.PHONY: all clean burn burn_fuses run

