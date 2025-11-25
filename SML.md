Simpletron Machine Language
Vamos criar um computador que chamaremos de Simpletron. Como seu nome indica, é uma máquina simples, mas, como logo veremos, uma máquina poderosa também. O Simpletron executa programas escritos na única linguagem que ele entende diretamente, isto é, Simpletron Machine Language, ou, abreviadamente, SML.

O Simpletron contém um acumulador - um "registrador especial" em que as informações são colocadas antes de o Simpletron utilizar essas informações em cálculos ou examiná-las de várias maneiras. Todas as informações no Simpletron são tratadas em termos de palavras. A palavra é um número decimal de quatro dígitos com um sinal como +3364, -1293, +0007, -0001, etc. O Simpletron é equipado com uma memória de 100 palavras e essas palavras são mencionadas por seus números de posição 00, 01, ..., 99.

Antes de executar um programa de SML, devemos carregar ou colocar o programa na memória. A primeira instrução de cada programa de SML é sempre colocada na posição 00. O simulador começará a executar as instruções a partir dessa posição.

Cada instrução escrita em SML ocupa uma palavra de memória do Simpletron (em consequência, as instruções são números decimais de quatro dígitos com sinal). Assumiremos que o sinal de uma instrução da SML é sempre mais, mas o sinal de uma palavra de dados pode ser mais ou menos. Cada posição na memória do Simpletron pode conter uma instrução, um valor de dados utilizado por um programa ou uma área de memória não utilizada (e portanto indefinida). Os primeiros dois dígitos de cada instrução da SML são os códigos de operação que especificam a operação a ser realizada. Os códigos de operação da SML estão resumidos na Tabela 1.

Tabela 1: códigos de operação da Simpletron Machine Language (SML)
Código de operação	Significado
Operações de entrada/saída:
READ = 10;	Lê uma palavra do teclado para uma posição específica da memória.
WRITE = 11;	Escreve na tela uma palavra de uma posição específica da memória.
Operações de carga/armazenamento:
LOAD = 20;	Carrega uma palavra de uma posição específica na memória para o acumulador.
STORE = 21;	Armazena uma palavra do acumulador em uma posição específica na memória.
Operações aritméticas:
ADD = 30;	Adiciona uma palavra de uma posição específica na memória à palavra no acumulador (deixa o resultado no acumulador).
SUBTRACT = 31;	Subtrai uma palavra de uma posição específica na memória à palavra no acumulador (deixa o resultado no acumulador).
DIVIDE = 32;	Divide a palavra que está no acumulador por uma palavra de uma posição específica na memória (deixa o resultado no acumulador).
MULTIPLY = 33;	Multiplica uma palavra de uma posição específica na memória pela palavra no acumulador (deixa o resultado no acumulador).
MODULE = 34;	Resto da divisão da palavra de uma posição específica na memória pela palavra no acumulador (deixa o resultado no acumulador).
Operações de transferência de controle:
BRANCH = 40;	Desvia para uma posição específica na memória.
BRANCHNEG = 41;	Desvia para uma posição específica na memória se o acumulador for negativo.
BRANCHZERO = 42;	Desvia para uma posição específica na memória se o acumulador for zero.
HALT = 43;	Finaliza o programa.
Os últimos dois dígitos de uma instrução da SML são os operandos - o endereço da posição da memória que contém a palavra à qual a operação se aplica.

Exercício 10.04
Desenvolva um programa em Simpletron Machine Language, que apresente a somatória dos números fornecidos pelo usuário, até que o usuário forneça o número zero. Por exemplo, caso os valores fornecidos pelo usuário sejam 1, 7, 4, 3 e 0, o programa deverá apresentar como resposta o valor 15, ou seja, 1 + 7 + 4 + 3.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta a somatória dos números fornecidos pelo usuário, até que o usuário forneça o número zero
Posição	Palavra	Instrução
00	+1008	read A
01	+2008	load A
02	+4206	branch zero to 06
03	+3009	add S
04	+2109	store S
05	+4000	branch to 00
06	+1109	write S
07	+4300	halt
08	+0000	variable A
09	+0000	variable S

Exercício 10.05
Desenvolva um programa em Simpletron Machine Language, que apresente o produto dos n primeiros números positivos. O valor de n será fornecido pelo usuário, devendo ser um valor inteiro e positivo. Por exemplo, caso o valor fornecido pelo usuário para n seja 5, o programa deverá apresentar como resposta o valor 120, ou seja, 1 * 2 * 3 * 4 * 5. Caso o usuário forneça um valor inválido para n, o programa deverá apresentar como resposta o valor -1.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta o fatorial de n
Posição	Palavra	Instrução
00	+1014	read N
01	+2014	load N
02	+4110	branch negative to 10
03	+4212	branch zero to 12
04	+3315	multiply F
05	+2115	store F
06	+2014	load N
07	+3016	add -1
08	+2114	store N
09	+4003	branch to 03
10	+1116	write -1
11	+4300	halt
12	+1115	write F
13	+4300	halt
14	+0000	variable N
15	+0001	variable F
16	-0001	constant -1

Exercício 10.06
Desenvolva um programa em Simpletron Machine Language, que apresente o produto dos números fornecidos pelo usuário, até que o usuário forneça o número zero. Por exemplo, caso os valores fornecidos pelo usuário sejam 1, 7, 4, 3 e 0, o programa deverá apresentar como resposta o valor 84, ou seja, 1 * 7 * 4 * 3.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta o produto dos números fornecidos pelo usuário, até que o usuário forneça o número zero
Posição	Palavra	Instrução
00	+1014	read A
01	+2014	load A
02	+4210	branch zero to 10
03	+2115	store S
04	+1014	read A
05	+2014	load A
06	+4212	branch zero to 12
07	+3315	multiply S
08	+2115	store S
09	+4004	branch to 04
10	+1114	write A
11	+4300	halt
12	+1115	write S
13	+4300	halt
14	+0000	variable A
15	+0000	variable S

Exercício 10.07
Desenvolva um programa em Simpletron Machine Language, que apresente a média dos n primeiros números positivos. O valor de n será fornecido pelo usuário, devendo ser um valor inteiro e positivo. Por exemplo, caso o valor fornecido pelo usuário para n seja 5, o programa deverá apresentar como resposta o valor 3, ou seja, (1 + 2 + 3 + 4 + 5) / 5. Caso o usuário forneça um valor inválido para n, o programa deverá apresentar como resposta o valor -1.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta a média dos n primeiros números positivos
Posição	Palavra	Instrução
00	+1017	read N
01	+2017	load N
02	+4114	branch negative to 14
03	+4214	branch zero to 14
04	+2118	store I
05	+3019	add S
06	+2119	store S
07	+2018	load I
08	+3116	subtract 1
09	+4211	branch zero to 11
10	+4004	branch to 04
11	+2019	load S
12	+3217	divide N
13	+2120	store M
14	+1120	write M
15	+4300	halt
16	+0001	constant 1
17	+0000	variable N
18	+0000	variable I
19	+0000	variable S
20	-0001	variable M

Exercício 10.07
Desenvolva um programa em Simpletron Machine Language, que apresente a média dos n primeiros números positivos. O valor de n será fornecido pelo usuário, devendo ser um valor inteiro e positivo. Por exemplo, caso o valor fornecido pelo usuário para n seja 5, o programa deverá apresentar como resposta o valor 3, ou seja, (1 + 2 + 3 + 4 + 5) / 5. Caso o usuário forneça um valor inválido para n, o programa deverá apresentar como resposta o valor -1.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta a média dos n primeiros números positivos
Posição	Palavra	Instrução
00	+1017	read N
01	+2017	load N
02	+4114	branch negative to 14
03	+4214	branch zero to 14
04	+2118	store I
05	+3019	add S
06	+2119	store S
07	+2018	load I
08	+3116	subtract 1
09	+4211	branch zero to 11
10	+4004	branch to 04
11	+2019	load S
12	+3217	divide N
13	+2120	store M
14	+1120	write M
15	+4300	halt
16	+0001	constant 1
17	+0000	variable N
18	+0000	variable I
19	+0000	variable S
20	-0001	variable M

Exercício 10.08
Desenvolva um programa em Simpletron Machine Language, que apresente a média dos números fornecidos pelo usuário, até que o usuário forneça o número zero. Por exemplo, caso os valores fornecidos pelo usuário sejam 2, 7, 4, 3 e 0, o programa deverá apresentar como resposta o valor 4, ou seja, (2 + 7 + 4 + 3) / 4.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta a média dos números fornecidos pelo usuário, até que o usuário forneça o número zero
Posição	Palavra	Instrução
00	+1021	read A
01	+2021	load A
02	+4213	branch zero to 13
03	+2122	store S
04	+2023	load N
05	+3020	add 1
06	+2123	store N
07	+1021	read A
08	+2021	load A
09	+4215	branch zero to 15
10	+3022	add S
11	+2122	store S
12	+4004	branch to 04
13	+1121	write A
14	+4300	halt
15	+2022	load S
16	+3223	divide N
17	+2124	store M
18	+1124	write M
19	+4300	halt
20	+0001	constant 1
21	+0000	variable A
22	+0000	variable S
23	+0000	variable N
24	+0000	variable M

Exercício 10.38
Desenvolva um programa em Simpletron Machine Language, que apresente a sequência de Tribonacci, definida recursivamente pela fórmula Fn = Fn-1 + Fn-2 + Fn-3, sendo F0 = 0, F1 = 1 e F2 = 1. O valor de n será fornecido pelo usuário, devendo ser um valor inteiro maior ou igual a zero. Por exemplo, caso o valor fornecido pelo usuário para n seja 6, o programa deverá apresentar como resposta a sequência de números 0 1 1 2 4 7 13. Caso o usuário forneça um valor inválido para n, o programa deverá apresentar como resposta o valor -1.

Solução do Exercício
Programa em Simpletron Machine Language que apresenta os primeiros n termos da sequência de Tribonacci
Posição	Palavra	Instrução
00	+1022	read N
01	+2022	load N
02	+4119	branch negative to 19
03	+1123	write A
04	+4220	branch zero to 20
05	+2023	load A
06	+3024	add B
07	+3025	add C
08	+2126	store D
09	+2024	load B
10	+2123	store A
11	+2025	load C
12	+2124	store B
13	+2026	load D
14	+2125	store C
15	+2022	load N
16	+3021	add -1
17	+2122	store N
18	+4003	branch to 03
19	+1121	write -1
20	+4300	halt
21	-0001	constant -1
22	+0000	variable N
23	+0000	variable A
24	+0001	variable B
25	+0001	variable C
26	+0000	variable D
