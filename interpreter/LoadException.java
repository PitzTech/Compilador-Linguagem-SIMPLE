/**
 * Exceção na leitura do arquivo contendo o código-fonte para a memória da Simpletron Machine Language (SML)
 */
public class LoadException extends Exception
{
  /**
   * Identificador de serialização da classe
   */
  private static final long serialVersionUID = 1L;

  /**
   * Constructs a new LoadException with null as its detail message
   */
  public LoadException()
  {
    super();
  }

  /**
   * Constructs a new LoadException with the specified detail message
   *
   * @param message the detail message
   */
  public LoadException(final String message)
  {
    super(message);
  }

  /**
   * Constructs a new LoadException with the specified detail message and cause
   *
   * @param message the detail message
   * @param cause the cause
   */
  public LoadException(final String message, final Throwable cause)
  {
    super(message, cause);
  }
}
