import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CalculadoraTest {

    @BeforeEach
    void setUp() {
    }

    @AfterEach
    void tearDown() {
    }
    // Pruebas para el método multiplicar
    @Test
    /**
     * Método multiplicar multiplicar numeros enteros
     */
    public void testMultiplicar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(6.0, calculadora.multiplicar(2.0, 3.0));
    }

    @Test

    /**
     * Método multiplicar multiplicar numeros decimales
     */
    public void testMultiplicarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(4.6, calculadora.multiplicar(2.0, 2.3));
    }

    @Test
    /**
     * Método multiplicar multiplicar numeros entero por negativo
     */
    public void testMultiplicarNegativoPorPositivo() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-6.0, calculadora.multiplicar(-2.0, 3.0));
    }
}