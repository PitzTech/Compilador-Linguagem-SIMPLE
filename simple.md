Linguagem de Programação SIMPLE
A linguagem de programação SIMPLE é uma linguagem simples, mas ainda poderosa e de alto nível, semelhante às versões iniciais da conhecida linguagem de programação BASIC. Cada instrução da linguagem de programação SIMPLE consiste em um número de linha e um comando da linguagem. Os números de linha devem aparecer em ordem crescente. Cada comando inicia com um das seguintes palavras reservadas da linguagem de programação SIMPLE: rem, input, let, print, goto, if/goto ou end.

Comandos da linguagem de programação SIMPLE
Comando	Descrição	Instrução de exemplo
rem	Qualquer texto depois do comando rem é apenas para fins de documentação e é ignorado pelo compilador.	50 rem isto é comentário
input	Exibe um ponto de interrogação para pedir ao usuário para inserir um inteiro. Lê esse inteiro do teclado e armazena o inteiro na variável especificada.	30 input x
let	Atribui a variável o valor da expressão aritmética simples.	80 let u = j - 56
print	Exibe o valor da variável especificada.	10 print w
goto	Transfere o comando do programa para a linha especificada.	70 goto 45
if/goto	Transfere o controle do programa para a linha especificada se a condição for verdadeira; caso contrário, continua a execução na próxima instrução.	35 if i == z goto 80
end	Termina a execução do programa.	99 end
Todos os comandos, exceto end, podem ser utilizados repetidamente. A linguagem de programação SIMPLE avalia apenas expressões inteiras que utilizam os operadores de adição (+), subtração (-), multiplicação (*), divisão inteira (/) e resto da divisão (%).

A linguagem de programação SIMPLE reconhece apenas letras minúsculas. Todos os caracteres em um arquivo na linguagem de programação SIMPLE devem estar em letras minúsculas (letras maiúsculas resultam em um erro de sintaxe, a menos que apareçam em uma instrução rem, caso em que são ignorados).

O nome de variável tem uma única letra. A linguagem de programação SIMPLE não permite nomes de variáveis descritivos, portanto as variáveis devem ser explicadas em comentários para indicar sua finalidade em um programa.

A linguagem de programação SIMPLE utiliza apenas variáveis inteiras. Não tem declarações de variáveis - a mera menção de um nome de variável em um programa faz com que a variável seja declarada e inicializada com zero.

A linguagem de programação SIMPLE utiliza a instrução condicional if/goto e a instrução incondicional goto para alterar o fluxo de controle durante a execução do programa. Se a condição na instrução if/goto for verdadeira, o controle é transferido para uma linha especifica do programa. Os seguintes operadores relacionais e de igualdade são válidos em uma instrução if/goto: maior que (>), maior ou igual a (>=), menor que (<), menor ou igual a (<=), igual a (==) e diferente de (!=).

O programa a seguir lê dois inteiros do teclado, armazena os valores nas variáveis a e b e calcula e imprime sua soma (armazenada na variável c).

10 rem determina e imprime a soma de dois inteiros
15 rem
20 rem lê os dois inteiros
30 input a
40 input b
45 rem
50 rem soma os inteiros e armazena o resultado em c
60 let c = a + b
65 rem
70 rem imprime o resultado
80 print c
90 rem termina a execução do programa
99 end
