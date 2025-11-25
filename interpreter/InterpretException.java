/**
 * Exceção na interpretação do código escrito em Simpletron Machine Language (SML)
 */
public class InterpretException extends Exception
{
  /**
   * Identificador de serialização da classe
   */
  private static final long serialVersionUID = 1L;

  /**
   * Constructs a new InterpretException with null as its detail message
   */
  public InterpretException()
  {
    super();
  }

  /**
   * Constructs a new InterpretException with the specified detail message
   *
   * @param message the detail message
   */
  public InterpretException(final String message)
  {
    super(message);
  }

  /**
   * Constructs a new InterpretException with the specified detail message and cause
   *
   * @param message the detail message
   * @param cause the cause
   */
  public InterpretException(final String message, final Throwable cause)
  {
    super(message, cause);
  }
}
