// written by Jonathan Hudgins
// 
//

// make sure that condition is true, otherwise exit the program
#define VALIDATE(cond)               if (!(cond)) FatalErrorMsg(#cond, __FILE__, __LINE__, "condition failed!"); else
#define VALIDATE_MSG(cond, msg, ...) if (!(cond)) FatalErrorMsg(#cond, __FILE__, __LINE__, msg, __VA_ARGS__); else

void FatalError(const char* cond, const char* filename, int line, const char* fmt, ...);

