// written by Jonathan Hudgins
// 
//
#include "mlerror.h"

// make sure that condition is true, otherwise exit the program
void FatalError(const char* cond, const char* filename, int line, const char* fmt, ...)
{
    va_list args;
    va_start(args, fmt);

    fprintf(stderr, "ERROR: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "condition:'%s', file:'%s:%d'\n", cond, filename, line);

    va_end (args);

    exit(1);
}


