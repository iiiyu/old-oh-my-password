ULIBINC	= include/
ULIBLIB = lib/

TARGET	= pwgen
OBJS	= pwgen.o

CC	?= gcc
CFLAGS	?= -c -O3 -g3 -W -Wall -Werror -pipe -DNDEBUG
LDFLAGS ?= -lulib

.c.o:
	$(CC) -I $(ULIBINC) $(CFLAGS) $< -o $@

.PNONY: all clean remove_bak

all: $(TARGET)

clean:
	rm -rf $(TARGET) $(OBJS)

remove_bak:
	find . -name "*~" | xargs rm -f

$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) -L $(ULIBLIB) $(LDFLAGS)
