#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <sys/types.h>

#define PTR(x) uint32_t

#define PACKED __attribute__((packed))

typedef struct {
  uint8_t index; // absolute index to identify part?
  uint8_t level; // level / quality?
  uint8_t unk1; // ?
  uint8_t category; // what kind of part it is?
  int32_t price;
  int32_t model; // model index
  PTR(char*) title;
} PACKED PartData;

typedef struct {
  uint32_t index;
  uint32_t pod_model; // "Podd"
  uint32_t pod_model_lod1; // "Malt": Good quality
  uint32_t pod_model_lod2; // "Malt": Medium quality
  uint32_t pod_model_lod3; // "Malt": Lowest quality
  PTR(char*) first_name;
  PTR(char*) last_name;
  float unkf1; // Olganix: Scale for pod to fit into Cantina hologram ?
  float unkf2; // Olganix: Scale for character to fit into Cantina hologram ?
  uint32_t unk1;
  uint32_t photo_sprite;
  uint32_t flag_sprite;
  uint32_t character_model;
} PACKED PodracerData;

typedef struct {
  float AntiSkid; // 0
  float TurnResponse; // 4
  float MaxTurnRate; // 8
  float Acceleration; // 12
  float MaxSpeed; // 16
  float AirbrakeInv; // 20
  float DecelInv; // 24
  float BoostThrust; // 28
  float HeatRate; // 32
  float CoolRate; // 36
  float HoverHeight; // 40
  float RepairRate; // 44
  float BumpMass; // 48
  float DmgImmunity; // 52
  float IsectRadius; // 56 //FIXME: Not sure
} PACKED PodracerHandlingData;

typedef struct {
  uint32_t track_model;
  uint32_t unk_spline; // Spline for this track - unknown usage
  uint8_t raceIndexOnPlanet;
  uint8_t planet;
  uint8_t trackFavorite; // This is only byte-accessed by the game
  uint8_t pad; // padding?
} PACKED TrackData;

static void* readExe(FILE* f, uint32_t offset, size_t size) {

  /*
    From `objdump -x swep1rcr.exe` for the patched US version:

    0 .text         000aa750  00401000  00401000  00000400  2**2
                    CONTENTS, ALLOC, LOAD, READONLY, CODE
    1 .rdata        000054a2  004ac000  004ac000  000aac00  2**2
                    CONTENTS, ALLOC, LOAD, READONLY, DATA
    2 .data         00023600  004b2000  004b2000  000b0200  2**2
                    CONTENTS, ALLOC, LOAD, DATA
    3 .rsrc         000017b8  00ece000  00ece000  000d3800  2**2
  */

  if ((offset >= 0x00401000) && (offset < (0x00401000 + 0x000aa750))) {
    // .text
    offset -= 0x00401000;
    offset += 0x00000400;
  } else if ((offset >= 0x004ac000) && (offset < (0x004ac000 + 0x000054a2))) {
    // .rdata
    offset -= 0x004ac000;
    offset += 0x000aac00;
  } else if ((offset >= 0x004b2000) && (offset < (0x004b2000 + 0x00023600))) {
    offset -= 0x004b2000;
    offset += 0x000b0200;
  } else {
    // .rsrc or unsupported
    printf("Unknown offset: 0x%08X\n", offset);
    //assert(false);
    return strdup("");
  }

  // Allocate space for the read
  void* data = malloc(size);

  // Read the data from the exe
  off_t previous_offset = ftell(f);
  fseek(f, offset, SEEK_SET);
  fread(data, size, 1, f);
  fseek(f, previous_offset, SEEK_SET);

  return data;
}

static char* escapeString(const char* string) {
  char* escaped_string = malloc(strlen(string) * 2 + 1);
  const char* s = string;
  char* d = escaped_string;
  while(*s != '\0') {
    if ((*s == '\"') || (*s == '\'') || (*s == '\\')) {
      *d++ = '\\';
    }
    *d++ = *s++;
  }
  *d = '\0';
  return escaped_string;
}

static char* reallocEscapedString(char* string) {
  char* escaped_string = escapeString(string);
  free(string);
  return escaped_string;
}

int main(int argc, char* argv[]) {

  FILE* f = fopen(argv[1], "rb");
  assert(f != NULL);

  // Read timestamp of binary to see which base version this is
  uint32_t timestamp;
  fseek(f, 216, SEEK_SET); //FIXME: Parse headers properly
  fread(&timestamp, 4, 1, f);

  // Now set the correct pointers for this binary
  uint32_t replacementPartOffset;
  uint32_t podracerOffset;
  uint32_t podracerHandlingOffset;
  uint32_t trackOffset;
  switch(timestamp) {
  case 0x3C60692C:
    replacementPartOffset = 0x4C1CB8;
    podracerOffset = 0x4C2700;
    podracerHandlingOffset = 0x4C2BB0;
    trackOffset = 0x4BFEE8;
    break;
  default:
    printf("Unsupported version of the game, timestamp 0x%08X\n", timestamp);
    return 1;
  }

  // Dump the list of replacement parts
  unsigned int replacementPartCount = 7 * 6; // 7 categories x 6 levels - FIXME: Read from file?
  PartData* replacementParts = readExe(f, replacementPartOffset, replacementPartCount * sizeof(PartData));
  unsigned int max_title_len = 0;
  for(unsigned int i = 0; i < replacementPartCount; i++) {
    PartData* d = &replacementParts[i];
    char* title = reallocEscapedString(readExe(f, d->title, 4096)); // FIXME: What length would be good here?
    if (strlen(title) > max_title_len) {
      max_title_len = strlen(title);
    }
    free(title);
  }
  printf("PartData replacementParts[] = {\n");
  for(unsigned int i = 0; i < replacementPartCount; i++) {
    PartData* d = &replacementParts[i];
    char* title = reallocEscapedString(readExe(f, d->title, 4096)); // FIXME: What length would be good here?
    printf("  { PART_%d, %d, 0x%02X, PART_CATEGORY_%d, %5d, \"%s\"%*s, MODEL_%d },\n", d->index, d->level, d->unk1, d->category, d->price, title, max_title_len - (int)strlen(title), "", d->model);
    free(title);
  }
  printf("};\n");
  free(replacementParts);

  printf("\n");

  // Dump podracer information
  unsigned int podracerCount = 23;
  PodracerData* podracers = readExe(f, podracerOffset, podracerCount * sizeof(PodracerData));
  printf("PodracerData podracers[] = {\n");
  for(unsigned int i = 0; i < podracerCount; i++) {
    PodracerData* d = &podracers[i];
    char* first_name = reallocEscapedString(readExe(f, d->first_name, 4096)); // FIXME: What length would be good here?
    char* last_name = reallocEscapedString(readExe(f, d->last_name, 4096)); // FIXME: What length would be good here?
    printf("  { PODRACER_%d, MODEL_%d, MODEL_%d, MODEL_%d, MODEL_%d, \"%s\", \"%s\", %ff, %ff, %d, SPRITE_%d, SPRITE_%d, MODEL_%d },\n",
      d->index,
      d->pod_model,
      d->pod_model_lod1,
      d->pod_model_lod2,
      d->pod_model_lod3,
      first_name, last_name,
      d->unkf1,
      d->unkf2,
      d->unk1,
      d->photo_sprite,
      d->flag_sprite,
      d->character_model);
    free(first_name);
    free(last_name);
  }
  printf("};\n");
  free(podracers);

  printf("\n");

  // Dump podracer handling data
  // There seems to be an additional AI handling profile at the end
  unsigned int podracerHandlingCount = podracerCount + 1;
  PodracerHandlingData* podracerHandling = readExe(f, podracerHandlingOffset, podracerHandlingCount * sizeof(PodracerHandlingData));
  printf("PodracerHandlingData podracerHandling[] = {\n");
  for(unsigned int i = 0; i < podracerHandlingCount; i++) {
    PodracerHandlingData* d = &podracerHandling[i];
    printf("  { %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff, %ff },",
      d->AntiSkid,
      d->TurnResponse,
      d->MaxTurnRate,
      d->Acceleration,
      d->MaxSpeed,
      d->AirbrakeInv,
      d->DecelInv,
      d->BoostThrust,
      d->HeatRate,
      d->CoolRate,
      d->HoverHeight,
      d->RepairRate,
      d->BumpMass,
      d->DmgImmunity,
      d->IsectRadius
    );
    if (i < podracerHandlingCount - 1) {
      printf(" // PODRACER_%d\n", i);
    } else {
      printf(" // AI preset?\n");
    }
  }
  printf("};\n");
  free(podracerHandling);

  printf("\n");

  // Dump list of tracks
  unsigned int trackCount = 25;
  TrackData* tracks = readExe(f, trackOffset, trackCount * sizeof(TrackData));
  printf("TrackData tracks[] = {\n");
  for(unsigned int i = 0; i < trackCount; i++) {
    TrackData* d = &tracks[i];
    printf("  { MODEL_%d, SPLINE_%d, %d, PLANET_%d, PODRACER_%d, 0x%02X },",
       d->track_model, d->unk_spline, d->raceIndexOnPlanet, d->planet, d->trackFavorite, d->pad
    );
    printf(" // TRACK_%d\n", i);
  }
  printf("};\n");
  free(tracks);




  fclose(f);

  return 0;
}
