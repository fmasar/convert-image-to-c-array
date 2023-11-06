# Convert image to C array in RGB565

Just a quick Python project to convert classic image format to C array (RGB565) for microcontrollers.
Converter is primarily for my graphical library AimiGUI, but it's basically universal.


AimiGUI image structures:
```
typedef struct {
      const uint16_t width;
      const uint16_t height;
      const uint16_t* data;
} AimiImageData;

typedef struct {
      const uint16_t width;
      const uint16_t height;
      const uint16_t* data;
      const uint8_t* comp;
} AimiImageDataRLE;

typedef struct {
      const uint16_t width;
      const uint16_t height;
      const uint8_t  type;
      const uint8_t* data;
} AimiMaskData;

typedef struct {
      const uint16_t width;
      const uint16_t height;
      const uint8_t  type;
      const uint8_t* data;
      const uint8_t* comp;
} AimiMaskDataRLE;

typedef struct {
      const AimiImageData* image;
      const AimiMaskData* mask;
} AimiImageMask;

typedef struct {
      const AimiImageDataRLE* image_rle;
      const AimiMaskData* mask;
} AimiImageRLEMask;

typedef struct {
      const AimiImageDataRLE* image_rle;
      const AimiMaskDataRLE* mask_rle;
} AimiImageMaskRLE;
```
