import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.Scanner;

/**
 * Classe responsável pela simulação da Simpletron Machine Language (SML)
 */
public class Simpletron
{
  /**
   * Quantidade de palavras armazenadas na memória
   */
  public static final int MEMORY_SIZE = 100;

  /**
   * Ler uma palavra do teclado para uma posição específica da memória
   */
  public static final int READ = 10;

  /**
   * Escrever na tela a palavra de uma posição específica da memória
   */
  public static final int WRITE = 11;

  /**
   * Carregar a palavra de uma posição específica da memória para o acumulador
   */
  public static final int LOAD = 20;

  /**
   * Armazenar a palavra do acumulador em uma posição específica na memória
   */
  public static final int STORE = 21;

  /**
   * Adicionar a palavra de uma posição específica na memória a palavra armazenada no acumulador
   */
  public static final int ADD = 30;

  /**
   * Subtrair a palavra de uma posição específica na memória a palavra armazenada no acumulador
   */
  public static final int SUBTRACT = 31;

  /**
   * Dividir a palavra de uma posição específica na memória a palavra armazenada no acumulador
   */
  public static final int DIVIDE = 32;

  /**
   * Multiplicar a palavra de uma posição específica na memória a palavra armazenada no acumulador
   */
  public static final int MULTIPLY = 33;

  /**
   * Resto da divisão da palavra de uma posição específica na memória a palavra armazenada no acumulador
   */
  public static final int MODULE = 34;

  /**
   * Desviar para uma posição específica na memória
   */
  public static final int BRANCH = 40;

  /**
   * Desviar para uma posição específica na memória se o acumulador for negativo
   */
  public static final int BRANCHNEG = 41;

  /**
   * Desviar para uma posição específica na memória se o acumulador for zero
   */
  public static final int BRANCHZERO = 42;

  /**
   * Finalizar o programa
   */
  public static final int HALT = 43;

  /**
   * Formato numérico dos dados da memória
   */
  private final DecimalFormat memoryFormatter;

  /**
   * Memória da Simpletron Machine
   */
  private int[] memory;

  /**
   * Acumulador da Simpletron Machine
   */
  private int accumulator;

  /**
   * Contador de instruções da Simpletron Machine
   */
  private int instructionCounter;

  /**
   * Código da operação
   */
  private int operationCode;

  /**
   * Operando
   */
  private int operand;

  /**
   * Leitor do teclado
   */
  private Scanner scanner;

  /**
   * Se a Simpletron Machine está em processamento
   */
  private boolean processing;

  /**
   * Inicializar a Simpletron Machine
   */
  public Simpletron()
  {
    processing = false;

    memory = new int[MEMORY_SIZE];

    for (var i = 0; i < memory.length; i++)
    {
      memory[i] = 0;
    }

    accumulator = 0;

    instructionCounter = 0;

    operationCode = 0;

    operand = 0;

    scanner = new Scanner(System.in);

    memoryFormatter = new DecimalFormat("+0000;-0000");
  }

  /**
   * Ler o arquivo contendo o código-binário para a memória da Simpletron Machine
   *
   * @throws LoadException problemas na leitura do código-binário
   */
  private void load() throws LoadException
  {
    try (final var leitor = new BufferedReader(new FileReader("binary.txt")))
    {
      var line = leitor.readLine();

      var counter = 0;

      while (line != null)
      {
        final var word = Integer.parseInt(line);

        if (word >= -9999 && word <= 9999)
        {
          memory[counter] = word;

          counter = counter + 1;
        }
        else
        {
          throw new NumberFormatException();
        }

        line = leitor.readLine();
      }
    }
    catch (final FileNotFoundException exception)
    {
      throw new LoadException("error : attempt to file not found!", exception);
    }
    catch (final IOException exception)
    {
      throw new LoadException("error : attempt to invalid file!", exception);
    }
    catch (final NumberFormatException exception)
    {
      throw new LoadException("error : attempt to invalid instruction!", exception);
    }

    System.out.println("Simpletron loading completed!");
  }

  /**
   * Interpretar a instrução READ
   */
  private void readInstruction()
  {
    System.out.print("input : ");

    var number = 0;

    try
    {
      number = Integer.parseInt(scanner.nextLine());
    }
    catch (final NumberFormatException exception)
    {
      number = Integer.MIN_VALUE;
    }

    if (number >= -9999 && number <= 9999)
    {
      memory[operand] = number;

      instructionCounter = instructionCounter + 1;
    }
    else
    {
      System.out.println("error : attempt to invalid number!");
    }
  }

  /**
   * Interpretar a instrução WRITE
   */
  private void writeInstruction()
  {
    System.out.print("output: ");

    System.out.println(memoryFormatter.format(memory[operand]));

    instructionCounter = instructionCounter + 1;
  }

  /**
   * Interpretar a instrução LOAD
   */
  private void loadInstruction()
  {
    accumulator = memory[operand];

    instructionCounter = instructionCounter + 1;
  }

  /**
   * Interpretar a instrução STORE
   */
  private void storeInstruction()
  {
    memory[operand] = accumulator;

    instructionCounter = instructionCounter + 1;
  }

  /**
   * Interpretar a instrução ADD
   *
   * @throws InterpretException problemas na interpretação da instrução ADD
   */
  private void addInstruction() throws InterpretException
  {
    accumulator = accumulator + memory[operand];

    if (accumulator >= -9999 && accumulator <= 9999)
    {
      instructionCounter = instructionCounter + 1;
    }
    else
    {
      throw new InterpretException("error : attempt to accumulator overflow!");
    }
  }

  /**
   * Interpretar a instrução SUBTRACT
   *
   * @throws InterpretException problemas na interpretação da instrução SUBTRACT
   */
  private void subtractInstruction() throws InterpretException
  {
    accumulator = accumulator - memory[operand];

    if (accumulator >= -9999 && accumulator <= 9999)
    {
      instructionCounter = instructionCounter + 1;
    }
    else
    {
      throw new InterpretException("error : attempt to accumulator overflow!");
    }
  }

  /**
   * Interpretar a instrução DIVIDE
   *
   * @throws InterpretException problemas na interpretação da instrução DIVIDE
   */
  private void divideInstruction() throws InterpretException
  {
    if (memory[operand] != 0)
    {
      accumulator = accumulator / memory[operand];

      instructionCounter = instructionCounter + 1;
    }
    else
    {
      throw new InterpretException("error : attempt to divide by zero!");
    }
  }

  /**
   * Interpretar a instrução MULTIPLY
   *
   * @throws InterpretException problemas na interpretação da instrução MULTIPLY
   */
  private void multiplyInstruction() throws InterpretException
  {
    accumulator = accumulator * memory[operand];

    if (accumulator >= -9999 && accumulator <= 9999)
    {
      instructionCounter = instructionCounter + 1;
    }
    else
    {
      throw new InterpretException("error : attempt to accumulator overflow!");
    }
  }

  /**
   * Interpretar a instrução MODULE
   *
   * @throws InterpretException problemas na interpretação da instrução MODULE
   */
  private void moduleInstruction() throws InterpretException
  {
    accumulator = accumulator % memory[operand];

    if (accumulator >= -9999 && accumulator <= 9999)
    {
      instructionCounter = instructionCounter + 1;
    }
    else
    {
      throw new InterpretException("error : attempt to accumulator overflow!");
    }
  }

  /**
   * Interpretar a instrução BRANCH
   */
  private void branchInstruction()
  {
    instructionCounter = operand;
  }

  /**
   * Interpretar a instrução BRANCHNEG
   */
  private void branchnegInstruction()
  {
    if (accumulator < 0)
    {
      instructionCounter = operand;
    }
    else
    {
      instructionCounter = instructionCounter + 1;
    }
  }

  /**
   * Interpretar a instrução BRANCHZERO
   */
  private void branchzeroInstruction()
  {
    if (accumulator == 0)
    {
      instructionCounter = operand;
    }
    else
    {
      instructionCounter = instructionCounter + 1;
    }
  }

  /**
   * Interpretar a instrução HALT
   */
  private void haltInstruction()
  {
    processing = false;
  }

  /**
   * Interpretar o código escrito em Simpletron Machine Language
   */
  private void interpret() throws InterpretException
  {
    System.out.println("Simpletron execution begins!");

    processing = true;

    while (processing)
    {
      final var instructionRegister = memory[instructionCounter];

      operationCode = instructionRegister / 100;

      operand = instructionRegister % 100;

      switch (operationCode)
      {
        case READ      : readInstruction();
                         break;

        case WRITE     : writeInstruction();
                         break;

        case LOAD      : loadInstruction();
                         break;

        case STORE     : storeInstruction();
                         break;

        case ADD       : addInstruction();
                         break;

        case SUBTRACT  : subtractInstruction();
                         break;

        case DIVIDE    : divideInstruction();
                         break;

        case MULTIPLY  : multiplyInstruction();
                         break;

        case MODULE    : moduleInstruction();
                         break;

        case BRANCH    : branchInstruction();
                         break;

        case BRANCHNEG : branchnegInstruction();
                         break;

        case BRANCHZERO: branchzeroInstruction();
                         break;

        case HALT      : haltInstruction();
                         break;

        default        : throw new InterpretException("error : attempt to unknown instruction!");
      }
    }

    System.out.println("Simpletron execution terminated!");
  }

  /**
   * Apresentar o dump da Simpletron Machine
   */
  private void dump()
  {
    final var variableFormatter = new DecimalFormat("   00");

    System.out.println();

    System.out.println("REGISTERS:");

    System.out.println(memoryFormatter.format(accumulator).substring(0, 5) + " Accumulator");

    System.out.println(variableFormatter.format(instructionCounter) + " Instruction Counter");

    System.out.println(memoryFormatter.format(memory[instructionCounter]) + " Instruction Register");

    System.out.println(variableFormatter.format(operationCode) + " Operation Code");

    System.out.println(variableFormatter.format(operand) + " Operand");

    System.out.println();

    System.out.println("MEMORY:");

    System.out.print(" ");

    for (var i = 0; i < 10; i++)
    {
      System.out.print("     " + i);
    }

    System.out.println();

    for (var i = 0; i < memory.length; i += 10)
    {
      System.out.print((i / 10) + " ");

      for (var j = i; j < i + 10; j++)
      {
        System.out.print(memoryFormatter.format(memory[j]) + " ");
      }

      System.out.println();
    }
  }

  /**
   * Executar a Simpletron Machine
   */
  public void execute()
  {
    System.out.println("Welcome to Simpletron!");

    try
    {
      load();

      interpret();
    }
    catch (final Exception exception)
    {
      System.out.println(exception.getMessage());

      System.out.println("Simpletron execution abnormally terminated!");
    }
    finally
    {
      dump();
    }
  }

  /**
   * Método principal da linguagem de programação Java
   *
   * @param args argumentos da linha de comando (não utilizado)
   */
  public static void main(String[] args)
  {
    final var simpletron = new Simpletron();

    simpletron.execute();
  }
}
