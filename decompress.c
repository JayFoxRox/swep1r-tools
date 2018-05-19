#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MAGIC(a1, a2, a3, a4) (((a1) << 24) | ((a2) << 16) | ((a3) << 8) | (a4))

static inline uint32_t swap32(uint32_t v) {
  return (((v & 0xFF0000) | (v >> 16)) >> 8) | (((v << 16) | (v & 0xFF00)) << 8);
}

//----- (0042D520) --------------------------------------------------------
// a1 = Input stream, note that this expects space for a window at a1-0x1000 which will be written to!
// a2 = Output stream
// LZ77 with a seperate 0x1000 window. No idea why this was done + the parameter choice for a1 is "odd", to say the least.
// Returns the pointer to the byte behind the last used output byte.
uint8_t* __cdecl sub_42D520(uint8_t* a1, uint8_t* a2) {
  uint8_t* v2 = a1;
  uint8_t* result = a2;
  uint8_t* v4 = &a1[-0x1000];
  int32_t v5 = 1;

  while(1) {
    // Read input byte
    uint8_t v20 = *v2++;

    // Loop over input bits
    for(int32_t v23 = 0; v23 < 8; v23++) {

      // Check if we want to use a byte copy instead of the window block copy
      if (v20 & (1 << v23)) {
        // Copy byte to output byte and to window
        uint8_t byte = *v2++;
        *result++ = byte;
        v4[v5] = byte;

        // Advance address in window
        v5 = (v5 + 1) & 0xFFF;
        continue;
      }

      // If this is block copy, get more parameters
      uint8_t v9 = *v2++; // 4 msb = number of bytes to copy; 4 lsb = source page (0x100 bytes) in window
      uint8_t v10 = *v2++; // byte offset within input page

      int32_t v11 = ((v9 & 0xF) * 0x100) + v10; // Get offset to source byte in window
      int32_t v12 = (v9 >> 4) & 0xF; // Get number of bytes to copy

      // If source offset is 0, it marks the end of the stream
      if (v11 == 0) {
        return result;
      }

      for(int32_t v14 = 0; v14 <= (v12 + 1); v14++) {
        // Copy byte to output and window
        uint8_t byte = v4[(v14 + v11) & 0xFFF];
        *result++ = byte;
        v4[v5] = byte;

        // Advance address in window
        v5 = (v5 + 1) & 0xFFF;
      }

    }
  }
}

int main(int argc, char* argv[]) {
  FILE* f;

  // Check for correct number of arguments
  if (argc != 3) {
    fprintf(stderr, "Usage: %s <input-file> <output-file>\n", argv[0]);
    return 1;
  }

  // Open file and get size
  f = fopen(argv[1], "rb");
  if (f == NULL) {
    fprintf(stderr, "Could not open input '%s'\n", argv[1]);
    return 1;
  }
  fseek(f, 0, SEEK_END);
  uint32_t in_size = ftell(f);
  fseek(f, 0, SEEK_SET);

  // Allocate space and read data
  // Note: We need 0x1000 bytes for the decompression window
  uint8_t* in = malloc(0x1000 + in_size);
  fread(&in[0x1000], in_size, 1, f);

  // Close input again
  fclose(f);

  // Do decompresion (or just copy if this is uncompressed)
  uint8_t* out = NULL;
  uint32_t out_size = 0;
  if (swap32(*(uint32_t*)&in[0x1000 + 0]) == MAGIC('C','o','m','p')) {    
    // Grab the output size from the header
    out_size = swap32(*(uint32_t*)&in[0x1000 + 8]);

    printf("Read %d bytes, decompressing %d bytes\n", in_size, out_size);

    // Do actual decompression
    out = malloc(out_size);
    uint8_t* end = sub_42D520(&in[0x1000 + 12], out);
    assert(out_size == end - out);
  } else {
    printf("Chunk is not compressed, copying %d bytes\n", in_size);

    // Do direct copy
    out_size = in_size;
    out = malloc(out_size);
    memcpy(out, &in[0x1000], in_size);
  }
  free(in);

  // Dump output buffer to file
  f = fopen(argv[2], "wb");
  if (f == NULL) {
    fprintf(stderr, "Could not open output '%s'\n", argv[2]);
    return 1;
  }
  fwrite(out, 1, out_size, f);
  fclose(f);

  free(out);

  return 0;
}
