%{
#include "parser.tab.h"
%}

%%

[0-9]+   { return NUM; }
"+"      { return PLUS; }
"-"      { return MINUS; }
"*"      { return TIMES; }
"/"      { return DIVIDE; }
"("      { return LPAREN; }
")"      { return RPAREN; }
[ \t\n]  { }
.        { }

%%

int yywrap(void) { return 1; }
