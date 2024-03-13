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
    // Pruebas para el método restar
    @Test
    /**
     * Método restar  restar enteros
     */
    public void testRestar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.0, calculadora.restar(8.0, 3.0));
    }

    @Test
    /**
     * Método restar  restar negativos
     */
    public void testRestarNegativos() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-5.0, calculadora.restar(-2.0, 3.0));
    }

    @Test
    /**
     * Método restar  restar decimales
     */
    public void testRestarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(6.0, calculadora.restar(6.3, 0.3));
    }

}