%{
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void yyerror(const char *s) {}
int yylex(void);
%}

%token NUM PLUS MINUS TIMES DIVIDE LPAREN RPAREN

%%
programa:
    expr  { }
;

expr:
    expr PLUS   term  { }
  | expr MINUS  term  { }
  | term               { }
;

term:
    term TIMES  factor { }
  | term DIVIDE factor { }
  | factor              { }
;

factor:
    NUM          { }
  | LPAREN expr RPAREN { }
;
%%

int main(void) {
    struct timespec inicio, fin;
    clock_gettime(CLOCK_MONOTONIC, &inicio);
    yyparse();
    clock_gettime(CLOCK_MONOTONIC, &fin);
    double ms = (fin.tv_sec - inicio.tv_sec) * 1000.0
              + (fin.tv_nsec - inicio.tv_nsec) / 1e6;
    printf("%.4f\n", ms);
    return 0;
}
