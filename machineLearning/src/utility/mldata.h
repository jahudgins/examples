// written by Jonathan Hudgins
// 
//
typedef enum
{
    MLTypeReal,
    MLTypeEnum
} MLDataType;

typedef struct
{
    char*       attributeName;
    MLDataType  attributeType;
    int         numEnumValues;
    char**      enumValues;
} MLDataAttribute;

typedef struct
{
    char*               relation;
    MLDataAttribute*    attributes;
    int                 numAttributes;
} MLDataHeader;

typedef struct
{
    const char*     filename;
    MLDataHeader    header;
    uint8_t*        data;
} MLData;

