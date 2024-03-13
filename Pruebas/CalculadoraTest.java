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
    // Pruebas para el método sumar
    /**
     * Método prueba suma sumar enteros
     */
    @Test
    public void testSumar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(25.0, calculadora.sumar(20.0, 5.0));
    }

    @Test
    /**
     * Método prueba suma sumar negativos
     */
    public void testSumarNegativos() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-5.0, calculadora.sumar(-2.0, -3.0));
    }

    @Test
    /**
     * Método prueba suma sumar decimales
     */
    public void testSumarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.5, calculadora.sumar(2.3, 0.2));
    }
}