/* The MIT License

   Copyright (C) 2011 Zilong Tan (tzlloch@gmail.com)

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
   ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
   CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <termio.h>
#include <getopt.h>
#include <ulib/aes.h>
#include <ulib/sha256sum.h>
#include <ulib/hexdump.h>

#define KEYBUFLEN 1024

#define CLOSE_NONSTD_FILE(tty) do {					\
		if ((tty) != stdin && (tty) != stdout && (tty) != stderr) \
			fclose(tty);					\
	} while (0)

const char *usage =
	"A Password Manager, by Zilong Tan (tzlloch@gmail.com)\n"
	"Usage: %s [options] [pw_str1 [pw_str2 ...]]\n"
	"  -k <key_file>     use specified key file, the default is 'pwgen.key'\n"
	"  -u <key_string>   set and update the key, this will modify key file\n"
	"  -h                show this message\n";

void read_till_nl(FILE *tty, char *buf, int len)
{
	char *nl;

	do {
		fgets(buf, len, tty);
	} while ((nl = strchr(buf, '\n')) == NULL);

	*nl = '\0';
}

int read_pwd(const char *msg, char *buf, int len)
{
	FILE *tty;
	struct termio tc;

	if ((tty = fopen("/dev/tty", "r")) == NULL)
		tty = stdin;

	fprintf(stderr, "%s", msg);

	if (ioctl(fileno(tty), TCGETA, &tc) == -1) {
		CLOSE_NONSTD_FILE(tty);
		return -1;
	}
	tc.c_lflag &= ~ECHO;
	if (ioctl(fileno(tty), TCSETA, &tc) == -1) {
		CLOSE_NONSTD_FILE(tty);
		return -1;
	}

	read_till_nl(tty, buf, len);

	tc.c_lflag |= ECHO;
	ioctl(fileno(tty), TCSETA, &tc);

	fprintf(stderr, "\n");

	CLOSE_NONSTD_FILE(tty);

	return 0;
}

int read_pwd2(char *buf, int len)
{
	char pwd[len];

	if (read_pwd("Password:", buf, len))
		return -1;
	if (read_pwd("Verify password:", pwd, sizeof(pwd)))
		return -1;
	if (buf[0] == '\0')
		return -1;  /* do not allow null password */
	if (strncmp(buf, pwd, len) == 0) {
#ifndef NDEBUG
		print_hex_dump_bytes("Verified password:", DUMP_PREFIX_OFFSET, buf, strlen(buf));
#endif
		return 0;
	}

#ifndef NDEBUG
	print_hex_dump_bytes("First :", DUMP_PREFIX_OFFSET, buf, strlen(buf));
	print_hex_dump_bytes("Second:", DUMP_PREFIX_OFFSET, pwd, strlen(pwd));
#endif

	return -1;
}

int set_key(const char *userkey, AES_KEY *key, int nbit, int enc)
{
	unsigned char hash[32] = { 0 };
	SHA256Context ctx;

	if (nbit != 128 && nbit != 192 && nbit != 256)
		return -1;

	SHA256Init(&ctx);
	SHA256Update(&ctx, userkey, strlen(userkey));
	SHA256Final(&ctx, hash);

	#ifndef NDEBUG
	print_hex_dump_bytes("User Key:", DUMP_PREFIX_OFFSET, hash, nbit >> 3);
	#endif

	if (enc) {
		if (AES_set_encrypt_key(hash, nbit, key))
			return -1;
	} else {
		if (AES_set_decrypt_key(hash, nbit, key))
			return -1;
	}

	return 0;
}

int read_key(AES_KEY *key, int nbit, int enc)
{
	char buf[KEYBUFLEN];

	if (read_pwd2(buf, sizeof(buf)))
		return -1;

	return set_key(buf, key, nbit, enc);
}

int load_key(const char *file, AES_KEY *key)
{
	FILE *fp = fopen(file, "rb");
	if (fp == NULL) {
		perror("cannot open file");
		return -1;
	}
	if (!fread(key, sizeof(*key), 1, fp)) {
		perror("cannot read key");
		fclose(fp);
		return -1;
	}
	fclose(fp);
	return 0;
}

int save_key(const char *file, const AES_KEY *key)
{
	FILE *fp = fopen(file, "wb");
	if (fp == NULL) {
		perror("cannot open file");
		return -1;
	}
	if (!fwrite(key, sizeof(*key), 1, fp)) {
		perror("cannot write key");
		fclose(fp);
		return -1;
	}
	fclose(fp);
	return 0;
}

void print_pw(const unsigned char *pw)
{
	static const char map[] =
		{ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
		  'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
		  'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
		  'W', 'X', 'Y', 'Z', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/', '^' };
	int i;

	for (i = 0; i < 8; ++i, pw += 3) {
		unsigned char code;
		putchar(map[pw[0] >> 2]);
		code = pw[0] << 4 | pw[1] >> 4;
		putchar(map[code & 0x3f]);
		code = pw[1] << 2 | pw[2] >> 6;
		putchar(map[code & 0x3f]);
		putchar(map[pw[2] & 0x3f]);
	}
	putchar('\n');
}

int gen_pw(const char *str, const AES_KEY *key)
{
	unsigned char *buf;
	unsigned char ivec[AES_BLOCK_SIZE] = { 0 };
	size_t len = strlen(str) + 2 * AES_BLOCK_SIZE;  /* at least two blocks */
	size_t nr  = len / AES_BLOCK_SIZE;

	buf = (unsigned char *) calloc(1, len);
	if (buf == NULL) {
		fprintf(stderr, "allocate password string failed\n");
		return -1;
	}

	strncpy((char *)buf, str, len);
	AES_cbc_encrypt(buf, buf, ivec, nr, key);
	print_pw(buf + nr * AES_BLOCK_SIZE - 24);
	free(buf);

	return 0;
}

int main(int argc, char *argv[])
{
	int oc, i;
	int save = 0;
	AES_KEY key;
	char line[4096];
	const char *keyfile = "pwgen.key";

	while ((oc = getopt(argc, argv, "k:u:h")) != -1) {
		switch (oc) {
		case 'k':
			keyfile = optarg;
			break;
		case 'u':
			if (set_key(optarg, &key, 256, 1)) {
				fprintf(stderr, "set key failed\n");
				return -1;
			}
			save = 1;
			break;
		case 'h':
			fprintf(stderr, usage, argv[0]);
			return 0;
		default:
			return -1;
		}
	}

	if (save) {
		if (save_key(keyfile, &key))
			fprintf(stderr, "key cannot be saved properly to %s\n", keyfile);
	} else {
		if (load_key(keyfile, &key)) {
			fprintf(stderr, "load key from %s failed, please enter manually\n", keyfile);
			if (read_key(&key, 256, 1)) {
				fprintf(stderr, "read key failed, exit\n");
				return -1;
			}
			if (save_key(keyfile, &key))
				fprintf(stderr, "key cannot be saved properly to %s\n", keyfile);
		}
	}

	/*
	 * now key is ready, proceed to produce passwords
	 */
	if (optind < argc) {
		for (i = optind; i < argc; ++i)
			gen_pw(argv[i], &key);
	} else {
		while (!ferror(stdin) && fgets(line, sizeof(line), stdin)) {
			size_t len = strlen(line);
			if (line[len - 1] == '\n')
				line[len - 1] = '\0';
			gen_pw(line, &key);
		}
	}

	return 0;
}
