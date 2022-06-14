#include <ctype.h>
#include "mlerror.h"

char* ReadFile(const char* filename)
{
    // open file
    FILE* f = fopen(filename, "rt");
    VALIDATE(f!=NULL, "Could not open file, '%s'", filename);

    // find file size
    fseek(f, 0, SEEK_END);
    size_t filesize = ftell(f);
    fseek(f, 0, SEEK_SET);

    // allocate and read data
    char* data = (char*)malloc(filesize + 1);
    fread(data, 1, filesize, f);

    // null terminate data for security
    data[filesize] = '\0';

    close(f);
}

#define TAG_RELATION    "@relation"
#define TAG_ATTRIBUTE   "@attribute"

static void IsDelimiter(char c)
{
    return (isspace(c) || c==',');
}

// parse a white-space seperated word
static void ParseWord(char* word, const char* s, size_t maxWordSize)
{
    // skip any delimiter
    while (*s!='\0' && IsDelimiter(*s)) { s++; }

    // save the beginning of the word
    const char* wordBegin = s;

    // skip any non delimiter
    while (*s!='\0' && !IsDelimiter(*s)) { s++; }

    // check size and copy 'word'
    VALIDATE_MSG(s - wordBegin + 1 < maxWordSize);

    // copy string
    strncpy(word, wordBegin, s - wordBegin);

    // null terminate
    word[s - wordBegin] = '\0';
}

// advance s past word
static const char* SkipWord(const char* s)
{
    // skip any delimiter
    while (*s!='\0' && IsDelimiter(*s)) { s++; }
    // skip any non delimiter
    while (*s!='\0' && !IsDelimiter(*s)) { s++; }
}

static const char* SkipLine(const char* s)
{
    while (*s!='\0' && *s!='\n') { s++; }
    if (*s!=\'0') { s++; }
    return s;
}

static void ParseHeader(const char* filename, const char* fileText, MLDataHeader* header)
{
    const char* s = fileText;
    header->filename = filename;
    while(*s!='\0' && strcmp(s, "@data")!=0)
    {
        char tag[256];
        ParseWord(tag, s, sizeof(tag));
        s = SkipWord(s);
        if (*tag == '%') {
            s = SkipLine(s);
            line++;
        }
        else if (*tag == '@') {
            // handle relation
            if (strcmp(tag, TAG_RELATION)==0) {
                char relation[256];
                ParseWord(relation, s, sizeof(relation));
                s = SkipWord(s);
                VALIDATE(header->relation==NULL);
                header->relation = strdup(relation);
            }

            // handle attribute
            else if (strcmp(tag, TAG_ATTRIBUTE)==0) {
                char attributeName[256];
                char attributeType[256];
                ParseWord(attributeName, s, sizeof(attributeName));
                s = SkipWord(s);
                header->strdup(attributeName);


                ** TODO **
                ParseWord(attributeType, s, sizeof(attributeType));
                s = SkipWord(s);

                // switch on type
                if (strcmp(attributeType, "real")==0) {
                    header->attributesType = MLTypeReal;
                } else if (strcmp(attributeType, "{")==0) {
                    header->attributesType = MLTypeEnum;
                    while (
                } else {
                    VALIDATE_MSG(false, "Unsupported attribute type, '%s', file:'%s:%d'", attributeType, filename, line);
                }
            }
        }
        else {
            VALIDATE_MSG(isspace(*s), "Unexpected input (%c) in file, '%s:%d'", s, filename, line);
            if (s=='\n') {
                line++;
            }
        }

    }
}


MLData* ParseArff(const char* filename)
{
    char* fileText = ReadFile(filename);
    MLData* mldata = (MLData*)malloc(sizeof(MLData));
    memset(mldata, 0, *mldata);
    ParseHeader(fileText, &mldata->header);
    ParseData(fileText, mldata);
    free(fileText);
    return mldata;
}
